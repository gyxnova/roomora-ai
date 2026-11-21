"""Database setup for Roomora AI.

Uses the standard-library sqlite3 module — no ORM, no extra packages.

Tables
------
designs             — one row per room design request (photo, budget, style, result).
telegraph_requests  — one row per Telegraph purchase we log (hackathon evidence).
                      Columns match section 7 rule 4 of the brief exactly.
"""
import sqlite3
import os
import config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _connect() -> sqlite3.Connection:
    """Return a sqlite3 connection to the configured database file."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

_CREATE_DESIGNS = """
CREATE TABLE IF NOT EXISTS designs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_filename   TEXT    NOT NULL,
    budget_inr       INTEGER NOT NULL,
    style            TEXT    NOT NULL,
    analysis_summary TEXT,
    design_plan      TEXT,
    prices           TEXT,
    status           TEXT    NOT NULL DEFAULT 'pending',
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""

# Columns match section 7 rule 4 exactly:
# id, created_at, item_name, message, http_status, status,
# cost_usd, job_id, answer, raw_json, network
_CREATE_TELEGRAPH_REQUESTS = """
CREATE TABLE IF NOT EXISTS telegraph_requests (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    item_name   TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    http_status INTEGER,
    status      TEXT,
    cost_usd    REAL,
    job_id      TEXT,
    answer      TEXT,
    raw_json    TEXT,
    network     TEXT    NOT NULL DEFAULT 'sepolia-testnet'
);
"""


def init_db():
    """Create all tables if they do not exist yet. Safe to run repeatedly."""
    with _connect() as conn:
        conn.execute(_CREATE_DESIGNS)
        conn.execute(_CREATE_TELEGRAPH_REQUESTS)
        conn.commit()


def reset_db():
    """Drop and recreate all tables. Only for development / tests."""
    with _connect() as conn:
        conn.execute("DROP TABLE IF EXISTS designs")
        conn.execute("DROP TABLE IF EXISTS telegraph_requests")
        conn.execute(_CREATE_DESIGNS)
        conn.execute(_CREATE_TELEGRAPH_REQUESTS)
        conn.commit()


# ---------------------------------------------------------------------------
# designs helpers
# ---------------------------------------------------------------------------

def insert_design(photo_filename, budget_inr, style,
                  analysis_summary, design_plan, prices, status="done") -> int:
    """Insert a design row and return its new id."""
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO designs
               (photo_filename, budget_inr, style,
                analysis_summary, design_plan, prices, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (photo_filename, budget_inr, style,
             analysis_summary, design_plan, prices, status),
        )
        conn.commit()
        return cur.lastrowid


def get_design(design_id: int) -> dict | None:
    """Fetch a single design by id, or None if not found."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM designs WHERE id = ?", (design_id,)
        ).fetchone()
        return dict(row) if row else None


def list_designs() -> list[dict]:
    """Return all designs, newest first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM designs ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# telegraph_requests helpers
# ---------------------------------------------------------------------------

def insert_telegraph_request(
    item_name: str,
    message: str,
    http_status: int | None = None,
    status: str | None = None,
    cost_usd: float | None = None,
    job_id: str | None = None,
    answer: str | None = None,
    raw_json: str | None = None,
    network: str = "sepolia-testnet",
) -> int:
    """Insert a telegraph_requests row and return its new id."""
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO telegraph_requests
               (item_name, message, http_status, status,
                cost_usd, job_id, answer, raw_json, network)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (item_name, message, http_status, status,
             cost_usd, job_id, answer, raw_json, network),
        )
        conn.commit()
        return cur.lastrowid


def list_telegraph_requests() -> list[dict]:
    """Return all telegraph_requests rows, newest first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM telegraph_requests ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def sum_telegraph_spend() -> float:
    """Return total cost_usd spent in this session (for the spend cap check)."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) AS total FROM telegraph_requests"
        ).fetchone()
        return float(row["total"]) if row else 0.0
