"""Roomora AI backend — FastAPI application.

Routes (section 10 of the brief):

    GET  /api/health     health check — returns vision_mode and pricing_mode
    GET  /api/catalog    list furniture items (INR prices)
    POST /api/design     create a room design (multipart: photo, budget_inr, style)
    GET  /api/designs    list all past design requests (newest first)
    GET  /api/receipts   list Telegraph purchase receipts from telegraph_requests
                         (always an empty list in mock/Phase-1 mode — never designs)

Validation:
    photo  — must be jpg / png / webp, under 8 MB
    budget — 5 000 to 5 000 000 INR
    style  — one of: minimalist, modern, japanese, scandinavian, luxury

Run with (from the backend/ directory):
    uvicorn main:app --reload
"""
import os
import uuid
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import config
import db
from services import designer, vision

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS    = {".jpg", ".jpeg", ".png", ".webp"}
MAX_PHOTO_BYTES       = config.MAX_UPLOAD_MB * 1024 * 1024
BUDGET_MIN            = 5_000
BUDGET_MAX            = 5_000_000
VALID_STYLES          = {"minimalist", "modern", "japanese", "scandinavian", "luxury"}


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create uploads dir relative to the working directory (backend/).
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    db.init_db()
    yield


app = FastAPI(title=config.APP_NAME, debug=config.DEBUG, lifespan=lifespan)

# Allow the React dev server to call this API without CORS errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    """Health check — returns current vision_mode and pricing_mode."""
    return {
        "status":       "ok",
        "app":          config.APP_NAME,
        "vision_mode":  config.VISION_MODE,
        "pricing_mode": config.PRICING_MODE,
    }


@app.get("/api/catalog")
def list_catalog():
    """List all furniture items in the catalog with INR prices."""
    from data import catalog
    return {"items": catalog.list_items()}


@app.post("/api/design")
def create_design(
    photo:      UploadFile = File(...),
    budget_inr: int        = Form(...),
    style:      str        = Form(...),
):
    """Create a new room design.

    Validates inputs, saves the photo, runs vision + designer pipeline,
    persists the result to the designs table, and returns the full JSON.
    """
    # --- Validate photo type -----------------------------------------------
    ext          = os.path.splitext(photo.filename or "")[1].lower()
    content_type = (photo.content_type or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES and ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and WebP images are accepted.",
        )

    # --- Validate photo size (read into memory once) -----------------------
    file_bytes = photo.file.read()
    if len(file_bytes) > MAX_PHOTO_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Photo is too large. Maximum allowed size is {config.MAX_UPLOAD_MB} MB.",
        )

    # --- Validate budget ---------------------------------------------------
    if not (BUDGET_MIN <= budget_inr <= BUDGET_MAX):
        raise HTTPException(
            status_code=422,
            detail=f"budget_inr must be between {BUDGET_MIN:,} and {BUDGET_MAX:,} INR.",
        )

    # --- Validate style ----------------------------------------------------
    style = style.strip().lower()
    if style not in VALID_STYLES:
        raise HTTPException(
            status_code=422,
            detail=f"style must be one of: {', '.join(sorted(VALID_STYLES))}.",
        )

    # --- Save photo to uploads/ --------------------------------------------
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path   = os.path.join(config.UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # --- Run the design pipeline -------------------------------------------
    analysis    = vision.analyze_room(unique_name)
    design_plan = designer.build_design_plan(budget_inr, style, analysis)
    prices      = [
        {
            "id":           item["id"],
            "name":         item["name"],
            "price_inr":    item["price_inr"],
            "price_source": item.get("price_source", "mock"),
            "receipt_id":   item.get("receipt_id"),
        }
        for item in design_plan.get("items", [])
    ]

    # --- Persist to designs table ------------------------------------------
    analysis_summary = analysis.get("note", str(analysis))
    design_id = db.insert_design(
        photo_filename   = unique_name,
        budget_inr       = budget_inr,
        style            = style,
        analysis_summary = analysis_summary,
        design_plan      = json.dumps(design_plan),
        prices           = json.dumps(prices),
        status           = "done",
    )

    # --- Return full design JSON -------------------------------------------
    return {
        "id":               design_id,
        "photo_filename":   unique_name,
        "budget_inr":       budget_inr,
        "style":            style,
        "analysis":         analysis,
        "analysis_summary": analysis_summary,
        "design_plan":      design_plan,
        "prices":           prices,
        "status":           "done",
    }


@app.get("/api/designs")
def list_designs():
    """List all past design requests, newest first."""
    return db.list_designs()


@app.get("/api/receipts")
def list_receipts():
    """List Telegraph purchase receipts from telegraph_requests, newest first.

    Returns an empty list in mock/Phase-1 mode (no Telegraph calls are made).
    NEVER returns designs — that is /api/designs.
    """
    rows = db.list_telegraph_requests()
    # Strip raw_json from the response (can be large; not needed by the UI).
    return [
        {
            "id":          r["id"],
            "created_at":  r["created_at"],
            "item_name":   r["item_name"],
            "status":      r["status"],
            "cost_usd":    r["cost_usd"],
            "job_id":      r["job_id"],
            "network":     r["network"],
        }
        for r in rows
    ]
