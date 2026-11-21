"""Roomora AI backend — FastAPI application.

Routes (section 10 of the brief):

    GET  /api/health     health check
    GET  /api/catalog    list furniture items (INR prices)
    POST /api/design     create a room design (multipart: photo, budget_inr, style)
    GET  /api/receipts   list all past designs (newest first)

Validation:
    photo  — must be jpg / png / webp, under 8 MB
    budget — 5 000 to 5 000 000 INR
    style  — one of: minimalist, modern, japanese, scandinavian, luxury
"""
import io
import os
import uuid
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import config
import db
from db import SessionLocal, Design
from services import designer, vision
from data import catalog

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_PHOTO_BYTES = 8 * 1024 * 1024          # 8 MB
BUDGET_MIN = 5_000
BUDGET_MAX = 5_000_000
VALID_STYLES = {"minimalist", "modern", "japanese", "scandinavian", "luxury"}


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
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
# Dependency
# ---------------------------------------------------------------------------

def get_db():
    """Yield a database session; always close it when the request finishes."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    """Health check — returns app name and current mode (mock / real)."""
    return {"status": "ok", "app": config.APP_NAME, "mode": config.MODE}


@app.get("/api/catalog")
def list_catalog():
    """List all furniture items with INR prices."""
    return {"items": catalog.list_items()}


@app.post("/api/design")
def create_design(
    photo: UploadFile = File(...),
    budget_inr: int = Form(...),
    style: str = Form(...),
    db_session: Session = Depends(get_db),
):
    """Create a new room design.

    Validates inputs, saves the photo, runs the vision + designer pipeline,
    persists the result, and returns the full design JSON.
    """
    # --- Validate photo type -------------------------------------------
    ext = os.path.splitext(photo.filename or "")[1].lower()
    content_type = (photo.content_type or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES and ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid file type. Only JPEG, PNG, and WebP images are accepted."
            ),
        )

    # --- Validate photo size (read into memory once) -------------------
    file_bytes = photo.file.read()
    if len(file_bytes) > MAX_PHOTO_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Photo is too large. Maximum allowed size is 8 MB.",
        )

    # --- Validate budget -----------------------------------------------
    if not (BUDGET_MIN <= budget_inr <= BUDGET_MAX):
        raise HTTPException(
            status_code=422,
            detail=(
                f"budget_inr must be between {BUDGET_MIN:,} and {BUDGET_MAX:,} INR."
            ),
        )

    # --- Validate style ------------------------------------------------
    style = style.strip().lower()
    if style not in VALID_STYLES:
        raise HTTPException(
            status_code=422,
            detail=(
                f"style must be one of: {', '.join(sorted(VALID_STYLES))}."
            ),
        )

    # --- Save photo to uploads/ ----------------------------------------
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(config.UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # --- Run the design pipeline ---------------------------------------
    analysis_summary = vision.analyze_room(unique_name)
    design_plan = designer.build_design_plan(budget_inr, style, analysis_summary)
    prices = [
        {"id": item["id"], "name": item["name"], "price_inr": item["price_inr"]}
        for item in design_plan.get("items", [])
    ]

    # --- Persist to database -------------------------------------------
    row = Design(
        photo_filename=unique_name,
        budget_inr=budget_inr,
        style=style,
        analysis_summary=analysis_summary,
        design_plan=str(design_plan),
        prices=str(prices),
        status="done",
    )
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)

    # --- Return full design JSON (section 5) ---------------------------
    return {
        "id": row.id,
        "photo_filename": row.photo_filename,
        "budget_inr": row.budget_inr,
        "style": row.style,
        "analysis_summary": analysis_summary,
        "design_plan": design_plan,
        "prices": prices,
        "status": row.status,
        "created_at": str(row.created_at),
    }


@app.get("/api/receipts")
def list_receipts(db_session: Session = Depends(get_db)):
    """List all past designs, newest first (the receipts / history page)."""
    rows = db_session.query(Design).order_by(Design.id.desc()).all()
    return [
        {
            "id": r.id,
            "photo_filename": r.photo_filename,
            "budget_inr": r.budget_inr,
            "style": r.style,
            "status": r.status,
            "created_at": str(r.created_at),
        }
        for r in rows
    ]
