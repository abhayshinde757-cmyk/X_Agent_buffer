# ⚡ X Command Center: Complete Technical Documentation

An enterprise-grade, AI-driven dashboard for X (Twitter) management. This application integrates real-time OneDrive synchronization, automated LLM content drafting, visual asset optimization, and deep-dive audience analytics.

---

## 🏗️ System Architecture & File Analysis

### 1. Core Server (`server.py`)
The **FastAPI** backbone of the application. It orchestrates all module interactions and exposes the following REST API:
- **`GET /`**: Serves the primary web dashboard.
- **`POST /api/rewrite`**: Accesses the AI suite to transform raw text into optimized X posts.
- **`POST /api/post`**: A standalone tool to post text and images directly to X via Buffer.
- **`POST /api/scrape`**: Triggers the Selenium scraper and the 10+ analysis agents to generate a 360° audience report.
- **`GET /api/excel/sync`**: The entry point for the **Excel Master Agent**. It pulls data from OneDrive and initializes auto-drafting.
- **`POST /api/excel/confirm`**: Finalizes a drafted event and pushes it live to X.

### 2. The AI Engine (`ai_rewriter.py` & `validator.py`)
Powered by **NVIDIA's Meta Llama 3.1 405B Instruct** model.
- **Drafting**: Uses a sophisticated system prompt to convert structured event data (Time, Venue, Speaker) into high-impact, emoji-rich posts under 280 characters.
- **Intelligence Reports**: Analyzes batches of scraped tweets to cluster topics, detect global sentiment, and generate a **Strategic Q&A** to solve audience pain points.
- **Validation**: Ensures every post strictly adheres to X's technical constraints.

### 3. Media Optimization (`image_processor.py`)
A specialized module using **Pillow (PIL)** to ensure visual quality.
- **GDrive Resolution**: Automatically converts viewable Google Drive links into direct binary download streams.
- **Contextual Padding**: Intelligently resizes images to fit a **16:9 (1200x675)** canvas, adding cinematic black bars to preserve the original aspect ratio without stretching.
- **Public Hosting**: Uploads the processed image to a public CDN (`uguu.se`), providing a stateless URL that the Buffer API can ingest for posting.

### 4. Audience Intelligence (`scraper.py`)
A robust **Selenium** automation layer.
- **Analysis Agents**: Features 10+ specialized logic hunters:
    - *Buzz Tracker*: Monitors volume and unique contributor growth.
    - *Sentiment Summary*: Real-time positive/negative/neutral ratio.
    - *Engagement Ranker*: Sorts tweets by Like/Retweet/Reply metrics.
    - *Advocate Tracker*: Identifies top community contributors.
    - *Problem Miner*: Uses regex to find audience questions and complaints.
- **Headless Mode**: Runs silently in the background using a dedicated Chrome profile.

### 5. Publishing Utility (`buffer_client.py` & `link_generator.py`)
- **Buffer Integration**: Communicates with the Buffer GraphQL API to queue and "Share Now" posts to X.
- **URL Extraction**: Parses complex GraphQL responses to retrieve the final X.com status link. If the link is still pending, it provides a smart fallback to the Buffer profile dashboard.

---

## 🔄 The "Excel Master Agent" Workflow (End-to-End)

The Excel Master Agent represents the most advanced workflow in the codebase, moving from third-party data to a live social post in seconds.

1.  **Trigger**: The user clicks "Sync Now" on the dashboard.
2.  **Ingestion**: `server.py` performs an `httpx` request to the **OneDrive Direct Link**.
3.  **Merge Logic**: The system loads the local `posts.xlsx` cache. It compares remote and local data using the `Event Title + Time` as a composite key. This ensures we **preserve the status** of previously drafted or posted events while still receiving new updates.
4.  **Dynamic Drafting**: Any row with a status of `"upcoming"` is immediately processed:
    - The LLM crafts a post.
    - The image is downloaded, padded, and re-hosted.
5.  **Review State**: The row is updated to `"Review Required"` in the local cache, making it visible as a card on the dashboard.
6.  **Confirmation**: When the user clicks "Finalize & Publish", the buffered data is pushed to X. The local state is updated to `"Posted"` and the final **Live Link** is saved to the Excel file.

---

## 🛠️ Configuration & Environment

### `config.py`
This file acts as the secure vault for your environment.
- **`EXCEL_FILE_PATH`**: Absolute path to the local runtime cache workbook.
- **`REMOTE_EXCEL_URL`**: The direct download URL for your OneDrive source.
- **`NVIDIA_API_KEY`**: Required for all Llama 3.1 features.
- **`API_KEY` & `CHANNEL_ID`**: Your Buffer credentials for X integration.

---

## 💻 Technical Setup

### Installation
```bash
pip install fastapi uvicorn pandas openpyxl httpx Pillow requests openai python-dotenv selenium webdriver-manager
```

### Execution
```bash
# Start the Integrated Command Center
python server.py
```
Visit: **[http://localhost:8000](http://localhost:8000)**

---

## 📄 License & Credits
MIT License | Developed for the **Advanced Agentic Coding** initiative at Google Deepmind.
