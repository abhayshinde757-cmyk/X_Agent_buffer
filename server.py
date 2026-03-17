import uvicorn
import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from config import EXCEL_FILE_PATH, REMOTE_EXCEL_URL

from ai_rewriter import rewrite_post
from validator import validate_post_text
from image_processor import pad_and_upload_image
from buffer_client import create_post
from link_generator import extract_post_link
from scraper import run_scraper_api

async def perform_excel_sync():
    """Triggered sync: Polls Remote Excel, merges with local status, drafts 'upcoming', and updates local cache."""
    async with httpx.AsyncClient() as client:
        try:
            # 1. Download from OneDrive
            print(f"INFO: Triggered Sync - Fetching remote Excel from OneDrive...")
            resp = await client.get(REMOTE_EXCEL_URL, follow_redirects=True, timeout=30.0)
            if resp.status_code == 200:
                # Load Remote Data
                from io import BytesIO
                remote_df = pd.read_excel(BytesIO(resp.content), engine='openpyxl')
                
                # Ensure essential columns exist in remote_df and are string type
                for col in ['status', 'link', 'processed_image', 'event title', 'time']:
                    if col not in remote_df.columns:
                        remote_df[col] = ""
                    remote_df[col] = remote_df[col].astype(str).replace('nan', '')

                # Load Local Data if exists
                if os.path.exists(EXCEL_FILE_PATH):
                    local_df = await asyncio.to_thread(pd.read_excel, EXCEL_FILE_PATH, engine='openpyxl')
                    
                    # Ensure essential columns exist in local_df and are string type
                    for col in ['status', 'link', 'processed_image', 'event title', 'time']:
                        if col not in local_df.columns:
                            local_df[col] = ""
                        local_df[col] = local_df[col].astype(str).replace('nan', '')

                    # Merge Logic: We want to keep remote events but PRESERVE local status/links for existing ones
                    if not remote_df.empty and not local_df.empty:
                        merged_df = remote_df.copy()
                        for idx, row in merged_df.iterrows():
                            # Look for this event in local (both as strings)
                            match = local_df[
                                (local_df['event title'] == row['event title']) & 
                                (local_df['time'] == row['time'])
                            ]
                            if not match.empty:
                                local_row = match.iloc[0]
                                # If remote is NOT 'upcoming', we preserve local status (Review Required/Posted)
                                # If remote IS 'upcoming', we ignore local and let it be re-processed
                                if row['status'].lower() != 'upcoming':
                                    if local_row['status'] in ['Review Required', 'Posted']:
                                        merged_df.at[idx, 'status'] = local_row['status']
                                        merged_df.at[idx, 'link'] = local_row['link']
                                        merged_df.at[idx, 'processed_image'] = local_row.get('processed_image', '')
                        df = merged_df
                    else:
                        df = remote_df
                else:
                    df = remote_df
                
                # Normalize and ensure columns
                for col in ['status', 'link', 'ai_draft', 'processed_image']:
                    if col not in df.columns:
                        df[col] = ""
                    df[col] = df[col].astype(str).replace('nan', '').replace('None', '')

                # Identify "upcoming" rows
                upcoming_mask = df['status'].str.lower().str.strip() == 'upcoming'
                upcoming_events = df[upcoming_mask]
                
                if not upcoming_events.empty:
                    print(f"INFO: Found {len(upcoming_events)} new upcoming events. Auto-processing...")
                    for index, row in upcoming_events.iterrows():
                        try:
                            # 1. AI Drafting
                            event_data = {
                                "event title": str(row.get("event title", "")),
                                "event description": str(row.get("event description", "")),
                                "location": str(row.get("location", "")),
                                "time": str(row.get("time", "")),
                                "speaker": str(row.get("speaker", "")),
                                "meetup link": str(row.get("meetup link", ""))
                            }
                            draft = await asyncio.to_thread(rewrite_post, event_data)
                            
                            # 2. Image Processing
                            orig_image = str(row.get("posterlink", "")).strip()
                            processed_url = ""
                            if orig_image and orig_image.lower() not in ['nan', 'none', '']:
                                try:
                                    processed_url = await asyncio.to_thread(pad_and_upload_image, orig_image)
                                except Exception as img_err:
                                    print(f"WARNING: Image processing failed: {img_err}")

                            # 3. Update row
                            df.at[index, 'status'] = 'Review Required'
                            df.at[index, 'ai_draft'] = draft 
                            df.at[index, 'link'] = "" # Clear stale Buffer output
                            df.at[index, 'processed_image'] = processed_url
                            
                            print(f"SUCCESS: Auto-processed draft for: {event_data['event title']}")
                        except Exception as row_err:
                            print(f"ERROR: Failed processing row {index}: {str(row_err)}")

                # Save back to local Excel
                await asyncio.to_thread(df.to_excel, EXCEL_FILE_PATH, index=False, engine='openpyxl')
                return True, ""
            else:
                return False, f"Remote Excel download failed: {resp.status_code}"
        except Exception as e:
            msg = f"Sync logic failure: {str(e)}"
            print(f"ERROR: {msg}")
            return False, msg

app = FastAPI(title="X Command Center API")

# --- Serve static files ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Pydantic Models ---
class RewriteRequest(BaseModel):
    text: str

class PostRequest(BaseModel):
    text: str
    image_url: Optional[str] = None

class ScrapeRequest(BaseModel):
    query: str

class ExcelConfirmRequest(BaseModel):
    index: int
    text: str
    image_url: Optional[str] = None


# --- Routes ---

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")


@app.post("/api/rewrite")
async def api_rewrite(req: RewriteRequest):
    """Takes raw draft text and returns AI-rewritten version."""
    try:
        rewritten = rewrite_post(req.text)
        validated = validate_post_text(rewritten)
        return {"success": True, "original": req.text, "rewritten": validated, "char_count": len(validated)}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"AI Rewriting failed: {str(e)}"}


@app.post("/api/post")
async def api_post(req: PostRequest):
    """Processes image (if any), posts to X via Buffer, and returns the Twitter link."""
    try:
        # Validate text
        validated = validate_post_text(req.text)

        # Process image if provided
        final_image_url = None
        if req.image_url and req.image_url.strip():
            final_image_url = pad_and_upload_image(req.image_url.strip())

        # Post to Buffer
        response = await asyncio.to_thread(create_post, validated, final_image_url)
        twitter_link = await asyncio.to_thread(extract_post_link, response)

        return {
            "success": True,
            "post_id": "",
            "twitter_link": twitter_link,
            "message": "Post created successfully!"
        }

    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Posting failed: {str(e)}"}


@app.post("/api/scrape")
async def api_scrape(req: ScrapeRequest):
    """Runs headless Selenium scraper + all analysis agents + AI Q&A."""
    try:
        result = run_scraper_api(req.query, headless=True)
        return {"success": True, "data": result}
    except RuntimeError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Scraping failed: {str(e)}"}


@app.get("/api/excel/sync")
async def api_excel_sync():
    """Triggers a full sync from remote, processes 'upcoming', then returns 'Review Required' events."""
    # 1. Trigger the actual sync/merge logic first
    success, error = await perform_excel_sync()
    if not success:
        return {"success": False, "error": error}

    # 2. Return current local state of 'Review Required'
    if not os.path.exists(EXCEL_FILE_PATH):
        return {"success": False, "error": "Excel file not found after sync."}

    try:
        df = pd.read_excel(EXCEL_FILE_PATH, engine='openpyxl')
        
        # Consistent dtype safety
        for col in ['status', 'event title', 'event description', 'location', 'time', 'speaker', 'meetup link', 'processed_image', 'link', 'ai_draft']:
            if col in df.columns:
                df[col] = df[col].astype(str).replace('nan', '').replace('None', '')
        
        review_required = df[df['status'] == 'Review Required']
        
        results = []
        for index, row in review_required.iterrows():
            event_data = {
                "index": int(index),
                "event title": str(row.get("event title", "")),
                "event description": str(row.get("event description", "")),
                "location": str(row.get("location", "")),
                "time": str(row.get("time", "")),
                "speaker": str(row.get("speaker", "")),
                "meetup link": str(row.get("meetup link", "")),
                "posterlink": str(row.get("processed_image", "")),
                "ai_draft": str(row.get("ai_draft", ""))
            }
            results.append(event_data)
        
        return {"success": True, "events": results}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/excel/confirm")
async def api_excel_confirm(req: ExcelConfirmRequest):
    """Publishes an Excel event and updates the sheet."""
    try:
        print(f"INFO: Confirming publish for index {req.index}...")
        response = await asyncio.to_thread(create_post, req.text, req.image_url)
        
        # Log the raw response for debugging
        print(f"DEBUG: Buffer API Response: {response}")
        
        twitter_link = await asyncio.to_thread(extract_post_link, response)
        print(f"INFO: Extracted link: {twitter_link}")

        df = pd.read_excel(EXCEL_FILE_PATH, engine='openpyxl')
        df.at[req.index, 'status'] = 'Posted'
        df.at[req.index, 'link'] = str(twitter_link)
        await asyncio.to_thread(df.to_excel, EXCEL_FILE_PATH, index=False, engine='openpyxl')
        print(f"SUCCESS: Local Excel updated for index {req.index}")

        return {"success": True, "link": str(twitter_link)}
    except Exception as e:
        print(f"ERROR: Excel Confirm Failed: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("\nSTARTING: X Command Center on http://localhost:8000\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
