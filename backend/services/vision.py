"""Vision service for Roomora AI (Phase 1 — MOCK mode).

Phase 1 uses a placeholder instead of a real vision model (OpenRouter). The
function below accepts a photo file name and returns a fake analysis. Phase 2
replaces this internals with a real OpenRouter call while keeping the same
signature so the rest of the app does not change.
"""
from config import MODE


def analyze_room(photo_filename):
    """Mock-analyze an uploaded room photo.

    Returns a short description. In Phase 2 this calls OpenRouter only when
    MODE == "real".
    """
    if MODE != "mock":
        # Phase 2 will fill in the real OpenRouter branch here.
        raise NotImplementedError("Real vision mode is not implemented yet (Phase 2).")

    return (
        f"Mock vision analysis of '{photo_filename}': a lived-in room with "
        "neutral walls, medium natural light, and clear wall space. "
        "No real vision model is used in Phase 1."
    )
