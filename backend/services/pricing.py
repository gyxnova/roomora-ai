"""Pricing service for Roomora AI.

Mock mode (Phase 1): returns prices from the local catalog with extra metadata
fields that the plan and frontend consume.

Telegraph mode (Phase 2): fill in the branch guarded by MODE == "real" to call
backend.telegraphprotocol.com and record a receipt_id + cost_usd.

Shape of every returned price dict (section 7):
    {
        "id":           str,
        "name":         str,
        "price_inr":    int,
        "price_source": "mock" | "telegraph",
        "receipt_id":   str | None,   # null until a real Telegraph receipt
        "cost_usd":     float,         # 0 in mock mode
        "cached":       bool,          # True when Telegraph returned a cache hit
    }
"""
from config import MODE
from data.catalog import find_item


def price_item(item_id: str) -> dict | None:
    """Return enriched pricing for a single catalog item, or None if not found.

    Mock mode   — reads the catalog and fills in zero/null for the Phase 2 fields.
    Telegraph mode — will call the real API (Phase 2).
    """
    if MODE == "real":
        # Phase 2 will POST to backend.telegraphprotocol.com here and capture
        # the receipt_id and actual USD cost.
        raise NotImplementedError("Phase 2")

    # --- Mock mode -------------------------------------------------------
    item = find_item(item_id)
    if not item:
        return None

    return {
        "id":           item["id"],
        "name":         item["name"],
        "price_inr":    item["price_inr"],
        "price_source": "mock",
        "receipt_id":   None,
        "cost_usd":     0,
        "cached":       False,
    }


def price_items(item_ids: list[str]) -> list[dict]:
    """Return enriched pricing for a list of item ids (skips missing ones)."""
    return [p for pid in item_ids if (p := price_item(pid)) is not None]
