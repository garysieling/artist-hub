"""
Pigment code search utility.
Find pigment codes by color name or get all pigments organized by color family.
"""

from typing import List, Dict, Any
from pigments import PIGMENT_CODES


def search_pigments_by_color(color_query: str) -> List[Dict[str, Any]]:
    """
    Search for pigments by color name or keyword.

    Args:
        color_query: Color name to search for (e.g., "yellow", "red", "blue")

    Returns:
        List of matching pigments with codes and RGB values
    """
    color_query = color_query.lower().strip()

    # Define color families and their keywords
    color_families = {
        "yellow": ["yellow", "arylide", "nickel", "isoindoline", "diarylide"],
        "red": ["red", "toluidine", "naphthol", "alizarin", "cadmium", "quinacridone"],
        "blue": ["blue", "phthalocyanine", "ultramarine", "indanthrene"],
        "green": ["green", "phthalocyanine"],
        "black": ["black", "carbon", "bone", "iron oxide", "mars"],
        "white": ["white", "zinc", "titanium", "plumbonacrite", "lead"],
        "violet": ["violet", "purple", "dioxazine", "quinacridone"],
        "orange": ["orange", "bismuth", "vanadate", "pyrazolone"],
        "brown": ["brown", "iron oxide"],
    }

    results = []

    # Search through PIGMENT_CODES
    for pigment_code, rgb_data in PIGMENT_CODES.items():
        code_lower = pigment_code.lower()

        # Check if query matches the pigment code
        if color_query.replace(" ", "") in code_lower.replace(" ", ""):
            results.append({
                "code": pigment_code,
                "rgb": rgb_data,
                "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                "name": f"{pigment_code} - Color"
            })

    # Also search by color family
    for family, keywords in color_families.items():
        if any(keyword in color_query for keyword in keywords):
            for pigment_code, rgb_data in PIGMENT_CODES.items():
                # Find pigments in this color family
                code_upper = pigment_code.upper()
                if family == "yellow" and code_upper.startswith("PY"):
                    if pigment_code not in [r["code"] for r in results]:
                        results.append({
                            "code": pigment_code,
                            "rgb": rgb_data,
                            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                            "name": f"{pigment_code} - {family.capitalize()}"
                        })
                elif family == "red" and code_upper.startswith("PR"):
                    if pigment_code not in [r["code"] for r in results]:
                        results.append({
                            "code": pigment_code,
                            "rgb": rgb_data,
                            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                            "name": f"{pigment_code} - {family.capitalize()}"
                        })
                elif family == "blue" and code_upper.startswith("PB"):
                    if pigment_code not in [r["code"] for r in results]:
                        results.append({
                            "code": pigment_code,
                            "rgb": rgb_data,
                            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                            "name": f"{pigment_code} - {family.capitalize()}"
                        })
                elif family == "green" and code_upper.startswith("PG"):
                    if pigment_code not in [r["code"] for r in results]:
                        results.append({
                            "code": pigment_code,
                            "rgb": rgb_data,
                            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                            "name": f"{pigment_code} - {family.capitalize()}"
                        })
                elif family == "black" and code_upper.startswith("PBK"):
                    if pigment_code not in [r["code"] for r in results]:
                        results.append({
                            "code": pigment_code,
                            "rgb": rgb_data,
                            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                            "name": f"{pigment_code} - {family.capitalize()}"
                        })
                elif family == "white" and code_upper.startswith("PW"):
                    if pigment_code not in [r["code"] for r in results]:
                        results.append({
                            "code": pigment_code,
                            "rgb": rgb_data,
                            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                            "name": f"{pigment_code} - {family.capitalize()}"
                        })
                elif family == "violet" and code_upper.startswith("PV"):
                    if pigment_code not in [r["code"] for r in results]:
                        results.append({
                            "code": pigment_code,
                            "rgb": rgb_data,
                            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                            "name": f"{pigment_code} - {family.capitalize()}"
                        })
                elif family == "orange" and code_upper.startswith("PO"):
                    if pigment_code not in [r["code"] for r in results]:
                        results.append({
                            "code": pigment_code,
                            "rgb": rgb_data,
                            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                            "name": f"{pigment_code} - {family.capitalize()}"
                        })
                elif family == "brown" and code_upper.startswith("PBR"):
                    if pigment_code not in [r["code"] for r in results]:
                        results.append({
                            "code": pigment_code,
                            "rgb": rgb_data,
                            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper(),
                            "name": f"{pigment_code} - {family.capitalize()}"
                        })

    return results


def get_all_pigments_by_family() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all pigments organized by color family.

    Returns:
        Dictionary mapping color families to lists of pigments
    """
    organized = {
        "Yellows": [],
        "Reds": [],
        "Blues": [],
        "Greens": [],
        "Blacks": [],
        "Whites": [],
        "Violets": [],
        "Oranges": [],
        "Browns": []
    }

    for pigment_code, rgb_data in PIGMENT_CODES.items():
        code_upper = pigment_code.upper()
        pigment_info = {
            "code": pigment_code,
            "rgb": rgb_data,
            "hex": f"#{rgb_data['r']:02x}{rgb_data['g']:02x}{rgb_data['b']:02x}".upper()
        }

        if code_upper.startswith("PY"):
            organized["Yellows"].append(pigment_info)
        elif code_upper.startswith("PR"):
            organized["Reds"].append(pigment_info)
        elif code_upper.startswith("PB"):
            organized["Blues"].append(pigment_info)
        elif code_upper.startswith("PG"):
            organized["Greens"].append(pigment_info)
        elif code_upper.startswith("PBK"):
            organized["Blacks"].append(pigment_info)
        elif code_upper.startswith("PW"):
            organized["Whites"].append(pigment_info)
        elif code_upper.startswith("PV"):
            organized["Violets"].append(pigment_info)
        elif code_upper.startswith("PO"):
            organized["Oranges"].append(pigment_info)
        elif code_upper.startswith("PBR"):
            organized["Browns"].append(pigment_info)

    # Remove empty families
    return {k: v for k, v in organized.items() if v}


if __name__ == "__main__":
    # Example usage
    print("=== Pigment Code Search Examples ===\n")

    # Search by color
    print("Searching for 'yellow':")
    results = search_pigments_by_color("yellow")
    for pigment in results:
        print(f"  {pigment['code']:12} -> RGB({pigment['rgb']['r']}, {pigment['rgb']['g']}, {pigment['rgb']['b']}) - {pigment['hex']}")

    print("\nSearching for 'red':")
    results = search_pigments_by_color("red")
    for pigment in results:
        print(f"  {pigment['code']:12} -> RGB({pigment['rgb']['r']}, {pigment['rgb']['g']}, {pigment['rgb']['b']}) - {pigment['hex']}")

    print("\nSearching for 'PY43':")
    results = search_pigments_by_color("PY43")
    for pigment in results:
        print(f"  {pigment['code']:12} -> RGB({pigment['rgb']['r']}, {pigment['rgb']['g']}, {pigment['rgb']['b']}) - {pigment['hex']}")

    print("\n=== All Pigments by Family ===\n")
    organized = get_all_pigments_by_family()
    for family, pigments in organized.items():
        print(f"{family}:")
        for pigment in pigments:
            print(f"  {pigment['code']:12} -> RGB({pigment['rgb']['r']}, {pigment['rgb']['g']}, {pigment['rgb']['b']:3}) - {pigment['hex']}")
        print()
