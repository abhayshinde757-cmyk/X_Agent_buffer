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
from config import EXCEL_FILE_PATH, REMOTE_EXCEL_URL

from ai_rewriter import rewrite_post
from validator import validate_post_text
from image_processor import pad_and_upload_image
from buffer_client import create_post
from link_generator import extract_post_link
from scraper import run_scraper_api

SYSTEM_EVENT_COLUMNS = {"ai_draft", "processed_image", "link", "posterlink", "status"}
EXPECTED_EXCEL_COLUMNS = [
    "status",
    "event title",
    "time",
    "posterlink",
    "event description",
    "location",
    "speaker",
    "meetup link",
    "ai_draft",
    "processed_image",
    "link",
]


def build_event_payload(row: pd.Series) -> dict:
    """Return all non-empty row values except internal system columns."""
    payload = {}
    for column, value in row.items():
        if str(column).strip().lower() in SYSTEM_EVENT_COLUMNS:
            continue

        text = str(value).strip()
        if text.lower() in {"", "nan", "none"}:
            continue

        payload[str(column)] = text
    return payload


def ensure_excel_cache_dir() -> None:
    os.makedirs(os.path.dirname(EXCEL_FILE_PATH), exist_ok=True)


def write_excel_cache(df: pd.DataFrame) -> None:
    ensure_excel_cache_dir()
    root, ext = os.path.splitext(EXCEL_FILE_PATH)
    tmp_path = f"{root}.tmp{ext or '.xlsx'}"
    df.to_excel(tmp_path, index=False, engine="openpyxl")
    os.replace(tmp_path, EXCEL_FILE_PATH)


def read_excel_cache() -> pd.DataFrame:
    return pd.read_excel(EXCEL_FILE_PATH, engine="openpyxl")


async def perform_excel_sync():
    """Strict dynamic sync: Fetches Remote Excel, filters ONLY 'upcoming', processes them, and overwrites local cache."""
    async with httpx.AsyncClient() as client:
        try:
            # 1. Download from OneDrive
            print(f"INFO: Triggered Sync - Fetching remote Excel from OneDrive...")
            resp = await client.get(REMOTE_EXCEL_URL, follow_redirects=True, timeout=30.0)
            if resp.status_code == 200:
                # Load Remote Data
                from io import BytesIO
                df = pd.read_excel(BytesIO(resp.content), engine='openpyxl')
                
                # Normalize columns safely
                for col in EXPECTED_EXCEL_COLUMNS:
                    if col not in df.columns:
                        df[col] = ""
                    df[col] = df[col].astype(str).replace('nan', '').replace('None', '')

                # STRICT FILTER: ONLY keep 'upcoming'
                upcoming_mask = df['status'].str.lower().str.strip() == 'upcoming'
                upcoming_events = df[upcoming_mask].copy()
                
                if upcoming_events.empty:
                    print(f"INFO: No upcoming events found. Data fetching skipped.")
                    # Still save an empty/clean set to local cache to clear old data
                    await asyncio.to_thread(write_excel_cache, upcoming_events)
                    return True, ""

                print(f"INFO: Processing {len(upcoming_events)} strictly upcoming events dynamically...")
                
                for index, row in upcoming_events.iterrows():
                    try:
                        # 1. AI Drafting
                        event_data = build_event_payload(row)
                        
                        draft = await asyncio.to_thread(rewrite_post, event_data)
                        
                        # 2. Image Processing
                        orig_image = str(row.get("posterlink", "")).strip()
                        processed_url = ""
                        if orig_image and orig_image.lower() not in ['', 'nan', 'none']:
                            try:
                                processed_url = await asyncio.to_thread(pad_and_upload_image, orig_image)
                            except Exception as img_err:
                                print(f"WARNING: Image processing failed: {img_err}")

                        # 3. Update row dynamically
                        upcoming_events.at[index, 'status'] = 'Review Required'
                        upcoming_events.at[index, 'ai_draft'] = draft 
                        upcoming_events.at[index, 'link'] = "" 
                        upcoming_events.at[index, 'processed_image'] = processed_url
                        
                        print(f"SUCCESS: Auto-processed dynamic draft: {event_data.get('event title', 'Untitled event')}")
                    except Exception as row_err:
                        print(f"ERROR: Processing row: {str(row_err)}")

                # Save ONLY the processed "upcoming" rows to local Excel as our active queue
                await asyncio.to_thread(write_excel_cache, upcoming_events)
                return True, ""
            else:
                return False, f"Remote download failed: {resp.status_code}"
        except PermissionError:
            msg = (
                f"Excel cache is locked: {EXCEL_FILE_PATH}. "
                "Close any app using the cache file and try again."
            )
            print(f"ERROR: {msg}")
            return False, msg
        except Exception as e:
            msg = f"Excel Sync Error: {str(e)}"
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
        df = read_excel_cache()
        
        # Consistent dtype safety
        for col in EXPECTED_EXCEL_COLUMNS:
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

        df = read_excel_cache()
        df.at[req.index, 'status'] = 'Posted'
        df.at[req.index, 'link'] = str(twitter_link)
        await asyncio.to_thread(write_excel_cache, df)
        print(f"SUCCESS: Local Excel updated for index {req.index}")

        return {"success": True, "link": str(twitter_link)}
    except Exception as e:
        print(f"ERROR: Excel Confirm Failed: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("\nSTARTING: X Command Center on http://localhost:8000\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
