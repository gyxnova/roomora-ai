"""Route tests for the Roomora AI FastAPI app.

Uses FastAPI's TestClient — no uvicorn server is needed.

Run with:  pytest backend/tests/test_routes.py -v
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.testclient import TestClient
from main import app
import db

client = TestClient(app)


def setup_function(function):
    """Reset the database before each test so tests are isolated."""
    db.reset_db()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health_returns_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["mode"] == "mock"


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def test_catalog_returns_items():
    resp = client.get("/api/catalog")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) > 0
    assert items[0]["price_inr"] > 0


# ---------------------------------------------------------------------------
# POST /api/design — happy path
# ---------------------------------------------------------------------------

def test_create_design_returns_full_payload():
    resp = client.post(
        "/api/design",
        data={"budget_inr": 50000, "style": "modern"},
        files={"photo": ("room.jpg", b"fake-image-bytes", "image/jpeg")},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["budget_inr"] == 50000
    assert body["style"] == "modern"
    assert body["status"] == "done"
    assert body["analysis_summary"]
    assert body["design_plan"]
    assert "prices" in body
    assert "id" in body
    assert "photo_filename" in body
    assert "created_at" in body


def test_create_design_uuid_filename_saved():
    """The saved filename should be a uuid hex, not the original upload name."""
    resp = client.post(
        "/api/design",
        data={"budget_inr": 100000, "style": "minimalist"},
        files={"photo": ("my-room.png", b"png-bytes", "image/png")},
    )
    assert resp.status_code == 200, resp.text
    saved = resp.json()["photo_filename"]
    # UUID hex has 32 chars; with extension it's 36 chars total
    assert saved != "my-room.png"
    assert saved.endswith(".png")


# ---------------------------------------------------------------------------
# POST /api/design — validation: bad file type
# ---------------------------------------------------------------------------

def test_create_design_rejects_bad_file_type():
    """A .txt / text/plain file must be rejected with 400."""
    resp = client.post(
        "/api/design",
        data={"budget_inr": 50000, "style": "modern"},
        files={"photo": ("notes.txt", b"not an image", "text/plain")},
    )
    assert resp.status_code == 400, resp.text
    assert "file type" in resp.json()["detail"].lower()


def test_create_design_rejects_pdf():
    resp = client.post(
        "/api/design",
        data={"budget_inr": 50000, "style": "modern"},
        files={"photo": ("doc.pdf", b"%PDF", "application/pdf")},
    )
    assert resp.status_code == 400, resp.text


# ---------------------------------------------------------------------------
# POST /api/design — validation: bad budget
# ---------------------------------------------------------------------------

def test_create_design_rejects_budget_too_low():
    """Budget below 5,000 must be rejected with 422."""
    resp = client.post(
        "/api/design",
        data={"budget_inr": 100, "style": "modern"},
        files={"photo": ("room.jpg", b"bytes", "image/jpeg")},
    )
    assert resp.status_code == 422, resp.text
    assert "budget_inr" in resp.json()["detail"].lower()


def test_create_design_rejects_budget_too_high():
    """Budget above 5,000,000 must be rejected with 422."""
    resp = client.post(
        "/api/design",
        data={"budget_inr": 9_999_999, "style": "modern"},
        files={"photo": ("room.jpg", b"bytes", "image/jpeg")},
    )
    assert resp.status_code == 422, resp.text


# ---------------------------------------------------------------------------
# POST /api/design — validation: bad style
# ---------------------------------------------------------------------------

def test_create_design_rejects_bad_style():
    resp = client.post(
        "/api/design",
        data={"budget_inr": 50000, "style": "bohemian"},
        files={"photo": ("room.jpg", b"bytes", "image/jpeg")},
    )
    assert resp.status_code == 422, resp.text
    assert "style" in resp.json()["detail"].lower()


def test_create_design_accepts_all_valid_styles():
    """Every valid style should return 200."""
    for style in ("minimalist", "modern", "japanese", "scandinavian", "luxury"):
        resp = client.post(
            "/api/design",
            data={"budget_inr": 50000, "style": style},
            files={"photo": ("room.jpg", b"bytes", "image/jpeg")},
        )
        assert resp.status_code == 200, f"style '{style}' failed: {resp.text}"


# ---------------------------------------------------------------------------
# GET /api/receipts
# ---------------------------------------------------------------------------

def test_receipts_empty_at_start():
    resp = client.get("/api/receipts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_receipts_contains_created_design():
    client.post(
        "/api/design",
        data={"budget_inr": 30000, "style": "scandinavian"},
        files={"photo": ("a.jpg", b"bytes", "image/jpeg")},
    )
    resp = client.get("/api/receipts")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    r = items[0]
    assert r["budget_inr"] == 30000
    assert r["style"] == "scandinavian"
    assert r["status"] == "done"
    assert "photo_filename" in r
    assert "created_at" in r


def test_receipts_newest_first():
    """Multiple designs should be returned newest (highest id) first."""
    for style in ("modern", "luxury"):
        client.post(
            "/api/design",
            data={"budget_inr": 50000, "style": style},
            files={"photo": ("room.jpg", b"bytes", "image/jpeg")},
        )
    items = client.get("/api/receipts").json()
    assert len(items) == 2
    assert items[0]["id"] > items[1]["id"]


# ---------------------------------------------------------------------------
# Old routes must NOT exist
# ---------------------------------------------------------------------------

def test_old_designs_route_gone():
    assert client.get("/designs").status_code == 404


def test_old_telegraph_route_gone():
    assert client.post("/telegraph-requests").status_code in (404, 405)
