"""Unit tests for the designer service.

Run with:  pytest backend/tests/test_designer.py -v
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.designer import (
    analyze_photo,
    build_design_plan,
    price_items,
    run_design,
)

# ---------------------------------------------------------------------------
# analyze_photo
# ---------------------------------------------------------------------------

def test_analyze_photo_returns_summary():
    summary = analyze_photo("living_room.jpg", "modern")
    assert isinstance(summary, str)
    assert "modern" in summary
    assert "Mock analysis" in summary


# ---------------------------------------------------------------------------
# build_design_plan — section 9 shape
# ---------------------------------------------------------------------------

def test_build_design_plan_has_section9_keys():
    plan = build_design_plan(50000, "modern", "a bright room")
    for key in ("style", "analysis", "items", "total_inr", "budget_inr",
                "within_budget", "alternatives_used", "notes"):
        assert key in plan, f"Missing key: {key}"


def test_build_design_plan_stays_within_budget():
    plan = build_design_plan(30000, "scandinavian", "a bright room")
    assert plan["total_inr"] <= 30000
    assert plan["budget_inr"] == 30000
    assert plan["within_budget"] is True
    assert plan["style"] == "scandinavian"
    assert "items" in plan


def test_build_design_plan_items_have_section7_fields():
    plan = build_design_plan(100000, "modern", "a room")
    assert plan["items"], "Expected at least one item for 'modern' with 100k budget"
    for item in plan["items"]:
        for key in ("id", "name", "price_inr", "price_source", "receipt_id",
                    "cost_usd", "cached"):
            assert key in item, f"Item missing key: {key}"
        assert item["price_source"] == "mock"
        assert item["receipt_id"] is None
        assert item["cost_usd"] == 0
        assert item["cached"] is False


def test_build_design_plan_picks_matching_style():
    """Items chosen for a known style should come from the catalog for that style."""
    plan = build_design_plan(100000, "modern", "a cozy room")
    # Only check items that weren't pulled in as alternatives.
    if not plan["alternatives_used"]:
        from data.catalog import find_item
        for item in plan["items"]:
            catalog_item = find_item(item["id"])
            assert "modern" in catalog_item["styles"]


def test_build_design_plan_total_matches_sum():
    plan = build_design_plan(200000, "scandinavian", "a room")
    calculated_total = sum(i["price_inr"] for i in plan["items"])
    assert plan["total_inr"] == calculated_total


def test_build_design_plan_alternatives_used_flag():
    """An obscure style with no catalog items should set alternatives_used=True."""
    plan = build_design_plan(500000, "nonexistent_style_xyz", "a room")
    assert plan["alternatives_used"] is True


def test_build_design_plan_within_budget_flag():
    plan = build_design_plan(1_000_000, "modern", "a room")
    assert plan["within_budget"] is True
    assert plan["total_inr"] <= 1_000_000


# ---------------------------------------------------------------------------
# price_items (delegates to pricing service)
# ---------------------------------------------------------------------------

def test_price_items_returns_prices():
    priced = price_items(["sofa-1", "chair-1"])
    assert len(priced) == 2
    prices = {p["id"]: p["price_inr"] for p in priced}
    assert prices["sofa-1"] == 45000
    assert prices["chair-1"] == 18000


def test_price_items_section7_fields():
    priced = price_items(["sofa-1"])
    assert len(priced) == 1
    p = priced[0]
    assert p["price_source"] == "mock"
    assert p["receipt_id"] is None
    assert p["cost_usd"] == 0
    assert p["cached"] is False


# ---------------------------------------------------------------------------
# run_design — full pipeline
# ---------------------------------------------------------------------------

def test_run_design_returns_full_payload():
    result = run_design("room.jpg", 50000, "modern")
    assert result["photo_filename"] == "room.jpg"
    assert result["budget_inr"] == 50000
    assert result["style"] == "modern"
    assert result["analysis_summary"]
    assert result["design_plan"]["items"]
    assert result["prices"]
    assert result["created_at"].endswith("Z")


def test_run_design_plan_has_section9_keys():
    result = run_design("room.jpg", 80000, "scandinavian")
    plan = result["design_plan"]
    for key in ("total_inr", "budget_inr", "within_budget", "alternatives_used", "notes"):
        assert key in plan, f"design_plan missing key: {key}"


def test_run_design_prices_match_plan_items():
    """result['prices'] should be the same list as result['design_plan']['items']."""
    result = run_design("room.jpg", 50000, "modern")
    assert result["prices"] == result["design_plan"]["items"]
