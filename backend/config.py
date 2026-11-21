"""Configuration for Roomora AI (section 6).

Reads every setting from environment variables (loaded from .env via
python-dotenv).  All defaults are set so the app works fully in mock mode
without a .env file — nothing secret is hard-coded here.

VISION_MODE  controls the vision service:
    "mock"       — Phase 1; returns fixed placeholder analysis.
    "openrouter" — Phase 3; calls OpenRouter with the configured model.

PRICING_MODE controls the pricing service:
    "mock"       — Phase 1; returns catalog estimates labelled MOCK.
    "telegraph"  — Phase 2; makes real Telegraph purchases on Sepolia testnet.
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
# Mode switches (independent per service — section 6)
# ---------------------------------------------------------------------------
VISION_MODE:  str = os.getenv("VISION_MODE",  "mock").lower()
PRICING_MODE: str = os.getenv("PRICING_MODE", "mock").lower()

# ---------------------------------------------------------------------------
# Database — SQLite (standard library sqlite3, no ORM)
# ---------------------------------------------------------------------------
DB_PATH: str = os.getenv("DB_PATH", "roomora.db")

# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "8"))

# ---------------------------------------------------------------------------
# Telegraph  (backend only — key never leaves this server)
# ---------------------------------------------------------------------------
TELEGRAPH_API_URL: str = os.getenv(
    "TELEGRAPH_API_URL",
    "https://backend.telegraphprotocol.com/agent/chat",
)
TELEGRAPH_API_KEY: str    = os.getenv("TELEGRAPH_API_KEY", "")
TELEGRAPH_NETWORK: str    = os.getenv("TELEGRAPH_NETWORK", "sepolia-testnet")

# Safety caps (section 6, section 7 rule 1 & 2)
TELEGRAPH_MAX_SPEND_USD_PER_CALL: float = float(
    os.getenv("TELEGRAPH_MAX_SPEND_USD_PER_CALL", "0.05")
)
TELEGRAPH_SESSION_CAP_USD: float = float(
    os.getenv("TELEGRAPH_SESSION_CAP_USD", "0.50")
)

# ---------------------------------------------------------------------------
# OpenRouter  (vision / image generation — Phase 3)
# ---------------------------------------------------------------------------
OPENROUTER_API_URL: str = os.getenv(
    "OPENROUTER_API_URL",
    "https://openrouter.ai/api/v1/chat/completions",
)
OPENROUTER_API_KEY: str    = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_VISION_MODEL: str = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "nvidia/nemotron-3.5-super-vl:free",
)

# ---------------------------------------------------------------------------
# Currency / pricing
# ---------------------------------------------------------------------------
DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "INR")
