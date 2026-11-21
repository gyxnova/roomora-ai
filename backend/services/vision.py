"""Vision service for Roomora AI.

VISION_MODE=mock (Phase 1):
    Returns fixed placeholder analysis — no network call, no key needed.

VISION_MODE=openrouter (Phase 3):
    Will call OpenRouter with the configured model and return real analysis.
    Not implemented yet — raises NotImplementedError("Phase 3").
"""
from config import VISION_MODE


def analyze_room(photo_filename: str) -> dict:
    """Analyse an uploaded room photo and return a structured dict.

    Shape (section 8):
        room_type         str
        style_hints       list[str]
        existing_furniture list[str]
        walls             str
        lighting          str
        approx_size       str
        vision_source     "mock" | "openrouter" | "fallback"

    Args:
        photo_filename: The filename (not full path) of the saved upload.
    """
    if VISION_MODE == "openrouter":
        # Phase 3 will POST to OpenRouter here with a base64 image_url part.
        raise NotImplementedError("Real vision mode is not implemented yet (Phase 3).")

    # --- MOCK mode: return fixed sample data, clearly labelled MOCK ----------
    return {
        "room_type": "living room",
        "style_hints": ["neutral", "open plan"],
        "existing_furniture": ["old sofa", "coffee table"],
        "walls": "neutral beige",
        "lighting": "medium natural light",
        "approx_size": "medium (~20 m²)",
        "vision_source": "mock",
        # Human-readable note so the UI can show the MOCK badge.
        "note": f"MOCK vision analysis of '{photo_filename}'. "
                "No real vision model is used in Phase 1.",
    }
