import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from ai_rewriter import rewrite_post
from validator import validate_post_text
from image_processor import pad_and_upload_image
from buffer_client import create_post
from link_generator import extract_post_link
from scraper import run_scraper_api

app = FastAPI(title="X Command Center API")

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Pydantic Models ---
class RewriteRequest(BaseModel):
    text: str

class PostRequest(BaseModel):
    text: str
    image_url: Optional[str] = None

class ScrapeRequest(BaseModel):
    query: str


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
        response = create_post(validated, final_image_url)

        # Parse the raw Buffer response directly
        try:
            post_data = response.get("data", {}).get("createPost", {})
            
            # Check for mutation error
            if "message" in post_data and "post" not in post_data:
                return {"success": False, "error": post_data["message"]}
            
            post_info = post_data.get("post", {})
            post_id = post_info.get("id", "Unknown")
            twitter_link = post_info.get("externalLink") or ""

            # If externalLink is None or empty, show a note
            if not twitter_link or str(twitter_link).strip() == "None":
                twitter_link = f"https://x.com — Link will be available shortly. Buffer ID: {post_id}"

            
            return {
                "success": True,
                "post_id": post_id,
                "twitter_link": twitter_link,
                "message": "Post created successfully!"
            }
        except Exception:
            # Fallback to the text-based parser
            result_text = extract_post_link(response)
            return {"success": True, "post_id": "", "twitter_link": str(result_text), "message": "Post created!"}

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


if __name__ == "__main__":
    print("\n🚀 X Command Center starting on http://localhost:8000\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
