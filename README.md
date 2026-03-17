# ⚡ X Command Center

An AI-powered command center for X (Twitter), enabling premium post creation, demand-based Excel synchronization, and deep audience analytics. Built with a sleek black-and-white theme using FastAPI, Selenium, and NVIDIA Llama 3.1.

---

## 🚀 Key Features

### 1. Post to X (AI Drafting)
- **AI Rewriting**: Automatically rewrites your raw drafts into engaging, high-impact X posts under 280 characters using NVIDIA's Llama 3.1 405B.
- **Dynamic Image Processor**: Converts any image URL (including Google Drive links) into a perfect 16:9 padded format hosted for X.
- **Instant Publishing**: Integrated with the Buffer API for seamless one-click posting.

### 2. Analytics & AI Q&A
- **Headless X Scraper**: Periodically fetches the latest tweets for #hashtags or @accounts without browser pop-ups.
- **Multi-Agent Analysis**:
    - **Sentiment Tracking**: Gauges audience atmosphere.
    - **Trending Topics**: Identifies recurring keywords.
    - **Advocate Detection**: Finds your most active supporters.
    - **Question Mining**: Extracts audience pain points.
- **Deep Insights**: Generates a consolidated "Intelligence Report" addressing audience problems with AI-driven solutions.

### 3. Excel Master Agent (Live Sync)
- **Demand-Based Sync**: Click "Sync Now" to fetch the latest event schedule from a remote OneDrive Excel file.
- **Auto-Drafting**: Automatically drafts X posts and processes images for any row marked as "upcoming".
- **Verified Mapping**: Seamlessly transitions posts from "Upcoming" to "Review Required" to "Posted" while providing a live, clickable X status link.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- **Python 3.8+**
- **Google Chrome** installed (for Selenium)
- **Buffer Account** (API Key and Channel ID)
- **NVIDIA API Key** (for Llama 3.1 access)

### 2. Configuration
The application is configured via `config.py`. Ensure it contains your valid credentials:
```python
API_KEY = "YOUR_BUFFER_API_KEY"
CHANNEL_ID = "YOUR_BUFFER_CHANNEL_ID"
GRAPHQL_URL = "https://api.buffer.com/graphql"
NVIDIA_API_KEY = "YOUR_NVIDIA_API_KEY"
EXCEL_FILE_PATH = "C:/path/to/posts.xlsx"
REMOTE_EXCEL_URL = "YOUR_ONEDRIVE_DOWNLOAD_LINK"
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn pandas openpyxl httpx Pillow requests openai python-dotenv selenium webdriver-manager
```

---

## 💻 Running the Application

### Start the Server
```bash
python server.py
```
After the server starts, navigate to the web dashboard:
👉 **[http://localhost:8000](http://localhost:8000)**

### First-Time Scraper Setup
On the first run of the Analytics tool, you may need to log in to X manually if your session isn't saved.
1. The scraper uses a dedicated profile directory (configurable in `scraper.py`).
2. Run the scraper once in windowed mode (set `headless=False` in `scraper.py`) to log in.

---

## 🛠️ Troubleshooting

### Server Port Conflict (Errno 10048)
If the server fails to start because port 8000 is occupied, use these PowerShell commands:
1. **Find PID**: `netstat -ano | findstr :8000`
2. **Kill Process**: `Stop-Process -Id <PID> -Force` (Replace `<PID>` with the result from step 1).

### Excel Sync Issues
Ensure your OneDrive link ends with `?download=1` for direct file access. If the sync button shows an error, check the console logs for specific download or parsing failures.

---

## 🎨 Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6)
- **AI**: NVIDIA API (Meta Llama 3.1 405B)
- **Automation**: Selenium WebDriver, Buffer GraphQL API
- **Data**: Pandas, OpenPyXL

---

## 📄 License
MIT License. Created for the Advanced Agentic Coding project.
