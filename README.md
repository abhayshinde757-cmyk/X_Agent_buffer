# ⚡ X Command Center

An AI-powered command center for X (Twitter), enabling premium post creation, automated scheduling, and deep audience analytics. Built with a sleek black-and-white theme using FastAPI and Selenium.

---

## 🚀 Key Features

### 1. AI-Powered Post Creation
- **NVIDIA Llama 3.1 Integration**: Automatically rewrites your drafts to be more engaging, interactive, and within the 280-character limit.
- **Dynamic Image Processing**: Paste any image URL (including Google Drive links). The system automatically pads images to a perfect 16:9 aspect ratio and hosts them for X.
- **One-Click Publishing**: Instant posting to X via Buffer API.

### 2. Deep X Analytics
- **Headless Scraper**: Runs a Selenium-based scraper in the background (no browser pop-ups) to fetch the latest tweets for any #hashtag or @account.
- **10+ Analysis Agents**:
    - **Sentiment Analysis**: Real-time mood tracking of the audience.
    - **Trending Topics**: Word-cloud style frequency analysis.
    - **Engagement Metrics**: Rank tweets by likes, reposts, and views.
    - **Question Mining**: Identify what your audience is asking.
    - **Event Feedback**: Categorized insights on content, venue, and speakers.
    - **Advocate Tracking**: Identify your most active contributors.

### 3. AI Q&A & Insights
- **Key Takeaways**: Automatically summarizes the scraped content into actionable bullet points.
- **Problem Solving**: Generates an AI-driven Q&A report to address audience queries and pain points discovered during scraping.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.8+
- Google Chrome installed (for Selenium)
- Buffer Account (for posting)
- NVIDIA API Key (for LLM features)

### 2. Configuration
Create a `config.py` in the root directory and add your keys:
```python
API_KEY = "YOUR_BUFFER_API_KEY"
CHANNEL_ID = "YOUR_BUFFER_CHANNEL_ID"
GRAPHQL_URL = "https://api.buffer.com/graphql"
NVIDIA_API_KEY = "YOUR_NVIDIA_API_KEY"
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn selenium webdriver-manager Pillow requests openai python-dotenv python-multipart
```

### 4. Chrome Profile Setup
The scraper uses a dedicated Chrome profile located at `D:\selenium_profile` (or your preferred path in `scraper.py`).
- Run `python scraper.py` once to log in to your X account manually. Subsequent runs will be headless and automated.

---

## 💻 Running the Application

### Start the Web Dashboard
```bash
python server.py
```
After the server starts, open your browser and navigate to:
**[http://localhost:8000](http://localhost:8000)**

### CLI Mode (Optional)
If you prefer the command line, you can run:
```bash
python app.py
```

---

---

## 🛠️ Troubleshooting

### ERR_ADDRESS_INVALID (0.0.0.0)
If the browser shows "This site can’t be reached" or `ERR_ADDRESS_INVALID` when visiting `0.0.0.0:8000`, it's because `0.0.0.0` is only for the server configuration.
- **Fix**: Always use **[http://localhost:8000](http://localhost:8000)** or **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### Server Port Conflict (Errno 10048)
If you see an error saying the port is already in use, run the following commands in your terminal (PowerShell) to kill the ghost process:

1. **Find the Process ID (PID) on port 8000**:
   ```powershell
   netstat -ano | findstr :8000
   ```
2. **Kill the process** (Replace `<PID>` with the number from the last column of the output):
   ```powershell
   taskkill /F /PID <PID>
   ```

---

## 🎨 Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla HTML5, CSS3 (Black & White Theme), JavaScript (ES6)
- **AI/LLM**: NVIDIA API (Meta Llama 3.1)
- **Automation**: Selenium WebDriver, Buffer GraphQL API
- **Image Processing**: Pillow (PIL)

---

---

## 🛠️ Git Collaboration

To sync this project with the parent repository, follow these steps:

### 1. Pushing Changes to Parent Repo
Once you've made changes and committed them locally, use this command to push to the main branch:
```bash
git push origin main
```

### 2. Fetching & Pulling Latest Data
To get the latest updates from the parent repository and merge them into your local workspace:
```bash
git fetch origin
git pull origin main
```

---

## 📄 License
MIT License. Created for the "Advanced Agentic Coding" project.
