"""Mock furniture catalog for Roomora AI (Phase 1).

Every item has an INR price so the design plan can show "live prices"
without calling any real pricing API. In Phase 2 this stays the same
shape; only the source of prices changes (mock -> live Telegraph).
"""

# Each item: id, name, category, style tags, price in INR.
CATALOG = [
    {"id": "sofa-1", "name": "Luna 3-Seater Sofa", "category": "seating",
     "styles": ["modern", "scandinavian", "minimalist"], "price_inr": 45000},
    {"id": "sofa-2", "name": "Cleo Velvet Sofa", "category": "seating",
     "styles": ["vintage", "bohemian"], "price_inr": 52000},
    {"id": "chair-1", "name": "Nova Accent Chair", "category": "seating",
     "styles": ["modern", "scandinavian"], "price_inr": 18000},
    {"id": "chair-2", "name": "Rattan Lounge Chair", "category": "seating",
     "styles": ["bohemian", "coastal"], "price_inr": 14000},
    {"id": "table-1", "name": "Oak Coffee Table", "category": "tables",
     "styles": ["scandinavian", "minimalist"], "price_inr": 22000},
    {"id": "table-2", "name": "Marble Side Table", "category": "tables",
     "styles": ["modern", "vintage"], "price_inr": 26000},
    {"id": "lamp-1", "name": "Bamboo Floor Lamp", "category": "lighting",
     "styles": ["bohemian", "scandinavian"], "price_inr": 7500},
    {"id": "lamp-2", "name": "Geometric Pendant", "category": "lighting",
     "styles": ["modern", "minimalist"], "price_inr": 9500},
    {"id": "rug-1", "name": "Jute Area Rug", "category": "rugs",
     "styles": ["bohemian", "coastal"], "price_inr": 11000},
    {"id": "rug-2", "name": "Wool Area Rug", "category": "rugs",
     "styles": ["modern", "vintage"], "price_inr": 15000},
]


def list_items():
    """Return the full catalog."""
    return list(CATALOG)


def items_for_style(style):
    """Return catalog items matching a given style (case-insensitive)."""
    style = (style or "").lower()
    return [item for item in CATALOG if style in item["styles"]]


def find_item(item_id):
    """Return a single catalog item by id, or None."""
    for item in CATALOG:
        if item["id"] == item_id:
            return item
    return None
