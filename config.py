import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = BASE_DIR / "runtime"

API_KEY = os.getenv("BUFFER_API_KEY", "")
CHANNEL_ID = os.getenv("BUFFER_CHANNEL_ID", "")

GRAPHQL_URL = os.getenv("BUFFER_GRAPHQL_URL", "")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

REMOTE_EXCEL_URL = os.getenv(
    "REMOTE_EXCEL_URL",
    "",
)

# Keep the writable queue separate from any workbook a user may open in Excel.
EXCEL_FILE_PATH = str(Path(os.getenv("EXCEL_FILE_PATH", RUNTIME_DIR / "posts_cache.xlsx")).resolve())
