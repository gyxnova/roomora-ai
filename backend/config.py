"""Configuration for Roomora AI (section 6).

Reads every setting from environment variables (loaded from .env via
python-dotenv).  All defaults are set so the app works out-of-the-box in
mock mode without a .env file — nothing secret is hard-coded here.

MODE controls the entire app:
    "mock"  — Phase 1; all services return deterministic placeholder data.
    "real"  — Phase 2; services call Telegraph / OpenRouter with real keys.
"""
import os
from dotenv import load_dotenv

# Load variables from .env into os.environ (safe no-op if file is absent).
load_dotenv()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
APP_NAME: str = os.getenv("APP_NAME", "roomora-ai")
DEBUG: bool   = os.getenv("DEBUG", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Mode switch — "mock" (Phase 1) or "real" (Phase 2)
# Every service reads MODE to decide whether to use placeholders or real APIs.
# ---------------------------------------------------------------------------
MODE: str = os.getenv("ROOMORA_MODE", "mock").lower()

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./roomora.db")

# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "backend/uploads")
# Maximum photo upload size in megabytes (enforced in main.py).
MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "8"))

# ---------------------------------------------------------------------------
# Telegraph  (backend only — key never leaves this server)
# ---------------------------------------------------------------------------
TELEGRAPH_API_URL: str = os.getenv(
    "TELEGRAPH_API_URL",
    "https://backend.telegraphprotocol.com/agent/chat",
)
TELEGRAPH_BEARER_KEY: str = os.getenv("TELEGRAPH_BEARER_KEY", "")
TELEGRAPH_NETWORK: str    = os.getenv("TELEGRAPH_NETWORK", "sepolia")
# Safety cap: maximum USD the agent may spend per Telegraph call.
TELEGRAPH_MAX_SPEND_USD: float = float(os.getenv("TELEGRAPH_MAX_SPEND_USD", "1.0"))

# ---------------------------------------------------------------------------
# OpenRouter  (vision / image generation)
# ---------------------------------------------------------------------------
OPENROUTER_API_URL: str = os.getenv(
    "OPENROUTER_API_URL",
    "https://openrouter.ai/api/v1/chat/completions",
)
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

# ---------------------------------------------------------------------------
# Currency / pricing
# ---------------------------------------------------------------------------
DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "INR")
