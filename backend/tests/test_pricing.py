"""Unit tests for the pricing service.

Run with:  pytest backend/tests/test_pricing.py -v
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from unittest.mock import patch

from services.pricing import price_item, price_items


# ---------------------------------------------------------------------------
# Mock mode (default)
# ---------------------------------------------------------------------------

def test_price_item_returns_dict_for_known_id():
    result = price_item("sofa-1")
    assert result is not None
    assert result["id"] == "sofa-1"
    assert result["price_inr"] == 45000


def test_price_item_returns_none_for_unknown_id():
    assert price_item("nonexistent-item-xyz") is None


def test_price_item_has_all_section7_fields():
    result = price_item("chair-1")
    assert result is not None
    for key in ("id", "name", "price_inr", "price_source", "receipt_id", "cost_usd", "cached"):
        assert key in result, f"Missing key: {key}"


def test_price_item_mock_field_values():
    result = price_item("lamp-1")
    assert result["price_source"] == "mock"
    assert result["receipt_id"] is None
    assert result["cost_usd"] == 0
    assert result["cached"] is False


def test_price_items_skips_missing():
    results = price_items(["sofa-1", "nonexistent-xyz", "chair-1"])
    assert len(results) == 2
    ids = {r["id"] for r in results}
    assert ids == {"sofa-1", "chair-1"}


def test_price_items_empty_list():
    assert price_items([]) == []


# ---------------------------------------------------------------------------
# Telegraph mode — must raise NotImplementedError("Phase 2")
# ---------------------------------------------------------------------------

def test_price_item_real_mode_raises_not_implemented():
    """When MODE == 'real', price_item must raise NotImplementedError('Phase 2')."""
    with patch("services.pricing.MODE", "real"):
        with pytest.raises(NotImplementedError, match="Phase 2"):
            price_item("sofa-1")
