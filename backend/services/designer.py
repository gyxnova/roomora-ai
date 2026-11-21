"""Designer service for Roomora AI.

Turns a room photo + budget + style into a design plan.

Phase 1: everything is mock — no real vision model, no real Telegraph, no
image generation. Phase 2 swaps the internals while keeping the same
function signatures so the routes and tests do not change.

Plan response shape (section 9):
    {
        "style":             str,
        "analysis":          str,
        "items":             list[PricedItem],   # each has section-7 fields
        "total_inr":         int,
        "budget_inr":        int,
        "within_budget":     bool,
        "alternatives_used": bool,
        "notes":             str,
    }

PricedItem (section 7):
    id, name, price_inr, price_source, receipt_id, cost_usd, cached
"""
from datetime import datetime, timezone

from data.catalog import items_for_style
from services import pricing


def analyze_photo(photo_filename: str, style: str) -> str:
    """Mock vision analysis of an uploaded room photo.

    Returns a short plain-English summary of what the 'model' saw.
    Phase 2 replaces this with a real OpenRouter call.
    """
    return (
        f"Mock analysis of '{photo_filename}': a {style}-style room with "
        "neutral walls, medium natural light, and space for a refresh. "
        "No real vision model is used in Phase 1."
    )


def build_design_plan(budget_inr: int, style: str, analysis_summary: str) -> dict:
    """Build a design plan: pick catalog items matching the style within budget.

    Items are priced via pricing.price_item so each carries the full section-7
    metadata (price_source, receipt_id, cost_usd, cached).

    The returned dict follows the section-9 shape.
    """
    candidates = items_for_style(style)
    chosen = []
    total = 0
    alternatives_used = False

    # Greedy pick: add items whose price fits the remaining budget.
    for item in candidates:
        priced = pricing.price_item(item["id"])
        if priced is None:
            continue
        if total + priced["price_inr"] <= budget_inr:
            chosen.append(priced)
            total += priced["price_inr"]

    # If nothing matched the style and budget, try the full catalog as fallback.
    if not chosen:
        from data.catalog import CATALOG
        for item in CATALOG:
            priced = pricing.price_item(item["id"])
            if priced is None:
                continue
            if total + priced["price_inr"] <= budget_inr:
                chosen.append(priced)
                total += priced["price_inr"]
                alternatives_used = True

    within_budget = total <= budget_inr

    notes_parts = ["Mock plan — prices are placeholder catalog values (Phase 1)."]
    if alternatives_used:
        notes_parts.append(
            f"No items found for style '{style}'; showing alternatives from the full catalog."
        )

    return {
        "style":             style,
        "analysis":          analysis_summary,
        "items":             chosen,
        "total_inr":         total,
        "budget_inr":        budget_inr,
        "within_budget":     within_budget,
        "alternatives_used": alternatives_used,
        "notes":             " ".join(notes_parts),
    }


def price_items(item_ids: list[str]) -> list[dict]:
    """Return enriched pricing for a list of item ids (delegates to pricing service)."""
    return pricing.price_items(item_ids)


def run_design(photo_filename: str, budget_inr: int, style: str) -> dict:
    """Run the full mock design pipeline end to end.

    Returns a dict with analysis, plan (section 9), and prices (section 7).
    """
    analysis = analyze_photo(photo_filename, style)
    plan = build_design_plan(budget_inr, style, analysis)
    prices = plan["items"]  # already enriched via pricing.price_item

    return {
        "photo_filename":  photo_filename,
        "budget_inr":      budget_inr,
        "style":           style,
        "analysis_summary": analysis,
        "design_plan":     plan,
        "prices":          prices,
        "created_at":      datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
