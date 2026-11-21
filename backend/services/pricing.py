"""Pricing service for Roomora AI.

PRICING_MODE=mock (Phase 1):
    Returns catalog estimates with price_source="mock" and zero cost_usd.

PRICING_MODE=telegraph (Phase 2):
    Will POST to Telegraph, record a receipt in SQLite, and return the live
    price.  Raises NotImplementedError("Phase 2") until that branch is built.

Shape of every returned price dict (section 7 rule 6):
    {
        "id":           str,
        "name":         str,
        "price_inr":    int,
        "price_source": "mock" | "telegraph_live" | "estimate_fallback",
        "receipt_id":   int | None,   # telegraph_requests row id; None in mock
        "cost_usd":     float,         # 0.0 in mock mode
        "cached":       bool,          # True when Telegraph returned a cache hit
    }
"""
from config import PRICING_MODE
from data.catalog import find_item


def price_item(item_id: str) -> dict | None:
    """Return enriched pricing for a single catalog item, or None if not found.

    Mock mode   — reads the catalog; fills zero / null for Phase 2 fields.
    Telegraph mode — will call Telegraph and record a receipt (Phase 2).
    """
    if PRICING_MODE == "telegraph":
        # Phase 2: POST to backend.telegraphprotocol.com, save receipt in
        # telegraph_requests table, return real price_inr + receipt_id.
        raise NotImplementedError("Phase 2")

    # --- Mock mode -----------------------------------------------------------
    item = find_item(item_id)
    if not item:
        return None

    return {
        "id":           item["id"],
        "name":         item["name"],
        "price_inr":    item["price_inr"],
        "price_source": "mock",
        "receipt_id":   None,   # no Telegraph receipt in mock mode
        "cost_usd":     0.0,
        "cached":       False,
    }


def price_items(item_ids: list[str]) -> list[dict]:
    """Return enriched pricing for a list of item ids (skips missing ones)."""
    return [p for pid in item_ids if (p := price_item(pid)) is not None]
