import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

load_dotenv(BASE_DIR / ".env")

SMART_RPA_API_URL = os.getenv("SMART_RPA_API_URL", "http://localhost:8000/api")
SMART_RPA_AGENT_TOKEN = os.getenv("SMART_RPA_AGENT_TOKEN", "agent-lima-01-token")
AGENT_NAME = os.getenv("AGENT_NAME", "AGENT-LIMA-01")
REQUEST_TIMEOUT = int(os.getenv("SMART_RPA_TIMEOUT", "30"))
POLL_INTERVAL = int(os.getenv("SMART_RPA_POLL_INTERVAL", "5"))
WEB_DATA_PATH = Path(os.getenv("SMART_RPA_WEB_DATA_PATH", PROJECT_DIR / "webExample" / "data" / "state.json"))
AGENT_STATE_PATH = Path(os.getenv("SMART_RPA_AGENT_STATE_PATH", BASE_DIR / "state.json"))
