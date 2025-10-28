"""
Pigment color code lookup utility.
Supports International Color Index (ICI) pigment codes used in professional art supplies.
"""

from typing import Optional, Dict, Any

# Common art pigment codes (International Color Index system)
PIGMENT_CODES = {
    # Yellows
    "PY 1": {"r": 255, "g": 255, "b": 0},      # Arylide Yellow
    "PY 3": {"r": 254, "g": 244, "b": 0},      # Arylide Yellow (greenish)
    "PY 43": {"r": 255, "g": 240, "b": 0},     # Nickel Titanium Yellow
    "PY 53": {"r": 245, "g": 235, "b": 0},     # Nickel-Complex Yellow
    "PY 83": {"r": 255, "g": 230, "b": 20},    # Diarylide Yellow
    "PY 109": {"r": 255, "g": 245, "b": 0},    # Isoindoline Yellow
    "PY 150": {"r": 220, "g": 200, "b": 0},    # Nickel Azo Yellow

    # Reds
    "PR 3": {"r": 255, "g": 0, "b": 0},        # Toluidine Red
    "PR 4": {"r": 200, "g": 10, "b": 10},      # Chlorinated Paranitraniline Red
    "PR 5": {"r": 220, "g": 20, "b": 20},      # Naphthol AS Red
    "PR 48": {"r": 190, "g": 0, "b": 0},       # Naphthol Red
    "PR 57": {"r": 220, "g": 30, "b": 30},     # Alizarin Crimson (synthetic)
    "PR 112": {"r": 255, "g": 100, "b": 100},  # Naphthol Red
    "PR 188": {"r": 200, "g": 0, "b": 0},      # Cadmium Red
    "PR 200": {"r": 180, "g": 40, "b": 40},    # Naphthamide Red
    "PR 202": {"r": 220, "g": 20, "b": 20},    # Quinacridone Red

    # Blues
    "PB 15": {"r": 0, "g": 50, "b": 255},      # Phthalocyanine Blue
    "PB 15:1": {"r": 0, "g": 30, "b": 250},    # Phthalocyanine Blue (greenish)
    "PB 15:3": {"r": 20, "g": 60, "b": 255},   # Phthalocyanine Blue (reddish)
    "PB 29": {"r": 0, "g": 0, "b": 200},       # Ultramarine Blue
    "PB 60": {"r": 0, "g": 100, "b": 200},     # Indanthrene Blue

    # Greens
    "PG 7": {"r": 0, "g": 150, "b": 100},      # Phthalocyanine Green
    "PG 36": {"r": 0, "g": 180, "b": 150},     # Phthalocyanine Green (yellowish)

    # Blacks
    "PBk 6": {"r": 20, "g": 20, "b": 20},      # Synthetic Iron Oxide Black
    "PBk 7": {"r": 10, "g": 10, "b": 10},      # Carbon Black
    "PBk 9": {"r": 15, "g": 15, "b": 15},      # Bone Black
    "PBk 11": {"r": 25, "g": 25, "b": 25},     # Mars Black

    # Whites
    "PW 4": {"r": 255, "g": 255, "b": 255},    # Zinc Oxide
    "PW 6": {"r": 255, "g": 255, "b": 255},    # Titanium Dioxide
    "PW 7": {"r": 250, "g": 250, "b": 250},    # Plumbonacrite (Lead White)

    # Violets/Purples
    "PV 1": {"r": 150, "g": 0, "b": 200},      # Dioxazine Violet
    "PV 3": {"r": 170, "g": 50, "b": 200},     # Dioxazine Violet (reddish)
    "PV 19": {"r": 160, "g": 30, "b": 180},    # Quinacridone Violet

    # Browns/Oranges
    "PO 20": {"r": 255, "g": 140, "b": 0},     # Bismuth Vanadate Orange
    "PO 36": {"r": 255, "g": 160, "b": 20},    # Pyrazolone Orange
    "PBr 7": {"r": 160, "g": 82, "b": 45},     # Synthetic Iron Oxide Brown
}


def lookup_pigment_code(color_name: str) -> Optional[Dict[str, Any]]:
    """
    Look up RGB values for a pigment code.
    Supports both "PY 43" and "PY43" formats (with or without space).

    Args:
        color_name: Pigment code like "PY 43", "PY43", "PR 188", etc.

    Returns:
        Dictionary with r, g, b keys if found, None otherwise.
    """
    # Check with exact match first (case-insensitive)
    color_upper = color_name.upper().strip()
    if color_upper in PIGMENT_CODES:
        return PIGMENT_CODES[color_upper]

    # Check with normalized spacing (PY43 -> PY 43)
    color_normalized = color_upper.replace(" ", "")
    for pigment_code, rgb in PIGMENT_CODES.items():
        if pigment_code.replace(" ", "") == color_normalized:
            return rgb

    return None
