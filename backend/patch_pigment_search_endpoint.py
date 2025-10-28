#!/usr/bin/env python3
"""
Patch script to add pigment search and lookup endpoints to app.py
"""

# Read the app.py file
with open("app.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# Find where to insert the new endpoints (after the existing /api/paints endpoints)
insert_index = None
for i, line in enumerate(lines):
    if '@app.post("/api/paints/lookup-color")' in line:
        # Find the end of this endpoint
        for j in range(i, len(lines)):
            if j > i and lines[j].startswith('@app') or (j > i and lines[j].startswith('def ') and '@app' not in lines[j-1]):
                insert_index = j
                break
        if insert_index is None:
            insert_index = i + 50  # fallback
        break

if insert_index is None:
    print("[FAIL] Could not find insertion point in app.py")
else:
    # Create the new pigment search endpoints
    new_endpoints = '''
@app.get("/api/pigments/search")
async def search_pigments(query: str):
    """Search pigments by color name (e.g., 'yellow', 'red', 'blue')"""
    try:
        from pigment_search import search_pigments_by_color
        results = search_pigments_by_color(query)
        return {"success": True, "query": query, "results": results}
    except Exception as e:
        logger.error(f"Error searching pigments: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/pigments/all")
async def get_all_pigments():
    """Get all pigments organized by color family"""
    try:
        from pigment_search import get_all_pigments_by_family
        organized = get_all_pigments_by_family()
        return {"success": True, "pigments": organized}
    except Exception as e:
        logger.error(f"Error getting all pigments: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/pigments/lookup/{pigment_code}")
async def lookup_pigment(pigment_code: str):
    """Look up a specific pigment code and return its RGB value"""
    try:
        from pigments import lookup_pigment_code
        result = lookup_pigment_code(pigment_code)

        if result:
            hex_color = f"#{result['r']:02x}{result['g']:02x}{result['b']:02x}".upper()
            return {
                "success": True,
                "code": pigment_code,
                "rgb": result,
                "hex": hex_color,
                "valid": True
            }
        else:
            return {
                "success": False,
                "code": pigment_code,
                "valid": False,
                "message": f"Pigment code '{pigment_code}' not found"
            }
    except Exception as e:
        logger.error(f"Error looking up pigment {pigment_code}: {e}")
        return {"success": False, "error": str(e)}

'''

    # Insert the new endpoints
    lines.insert(insert_index, new_endpoints)

    # Write back to file
    with open("app.py", "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("[OK] Successfully added pigment search endpoints to app.py")
    print("[OK] File saved successfully")
    print("\nNew Pigment API Endpoints:")
    print("  GET /api/pigments/search?query=yellow")
    print("  GET /api/pigments/all")
    print("  GET /api/pigments/lookup/{pigment_code}")
