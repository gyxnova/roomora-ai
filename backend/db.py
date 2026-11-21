"""Database setup for Roomora AI.

Uses SQLite (a single file database, no separate server needed) via SQLAlchemy.
Creates two tables:

* designs        — one row per room design request (photo, budget, style, result).
* telegraph_requests — one row per Telegraph purchase request we log.

Phase 1 keeps this simple: synchronous SQLAlchemy SessionLocal and a helper
to initialise the tables on startup.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

# SQLAlchemy engine. check_same_thread=False lets SQLite be used across
# FastAPI request threads during development.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

# SessionLocal: each request gets its own database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models.
Base = declarative_base()


class Design(Base):
    """A room design request and its result."""
    __tablename__ = "designs"

    id = Column(Integer, primary_key=True, index=True)
    # Original uploaded photo file name.
    photo_filename = Column(String, nullable=False)
    # User's budget in INR.
    budget_inr = Column(Integer, nullable=False)
    # Selected style (e.g. "modern", "scandinavian").
    style = Column(String, nullable=False)
    # Mock vision analysis summary (Phase 1).
    analysis_summary = Column(Text, nullable=True)
    # Mock design plan JSON (Phase 1).
    design_plan = Column(Text, nullable=True)
    # Mock list of furniture prices (Phase 1).
    prices = Column(Text, nullable=True)
    # Status of the whole pipeline: pending / done / failed.
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class TelegraphRequest(Base):
    """A Telegraph purchase request we have logged (real in Phase 2)."""
    __tablename__ = "telegraph_requests"

    id = Column(Integer, primary_key=True, index=True)
    # Links back to the design this purchase belongs to.
    design_id = Column(Integer, ForeignKey("designs.id"), nullable=False, index=True)
    # What was requested (item, quantity, max spend).
    payload = Column(Text, nullable=False)
    # Telegraph response we received.
    response = Column(Text, nullable=True)
    # sent / failed
    status = Column(String, default="sent", nullable=False)
    created_at = Column(DateTime, server_default=func.now())


def init_db():
    """Create all tables if they do not exist yet. Safe to run repeatedly."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a database session and close it when done (FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """Drop and recreate all tables. Only for development / tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
