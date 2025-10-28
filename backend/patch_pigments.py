#!/usr/bin/env python3
"""
Patch script to add pigment code support to app.py
This script modifies the lookup_color_by_name function to use the pigments module
"""

import re

# Read the app.py file
with open("app.py", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Define the old function
old_function = '''def lookup_color_by_name(color_name: str) -> Optional[Dict[str, Any]]:
    """
    Try to find RGB values for a color name using webcolors library.
    Returns dict with rgb values if found, None otherwise.
    """
    try:
        # Try CSS3 colors first
        rgb = webcolors.name_to_rgb(color_name.lower())
        return {"r": rgb.red, "g": rgb.green, "b": rgb.blue}
    except ValueError:
        # Try HTML4 colors
        try:
            rgb = webcolors.name_to_rgb(color_name.lower(), spec='html4')
            return {"r": rgb.red, "g": rgb.green, "b": rgb.blue}
        except ValueError:
            return None'''

# Define the new function
new_function = '''def lookup_color_by_name(color_name: str) -> Optional[Dict[str, Any]]:
    """
    Try to find RGB values for a color name using webcolors library or pigment codes.
    Supports standard CSS color names, HTML4 colors, and art pigment codes (PY, PR, PB, etc).
    Returns dict with rgb values if found, None otherwise.
    """
    # Try pigment codes first
    try:
        from pigments import lookup_pigment_code
        pigment_result = lookup_pigment_code(color_name)
        if pigment_result:
            return pigment_result
    except ImportError:
        pass

    try:
        # Try CSS3 colors first
        rgb = webcolors.name_to_rgb(color_name.lower())
        return {"r": rgb.red, "g": rgb.green, "b": rgb.blue}
    except ValueError:
        # Try HTML4 colors
        try:
            rgb = webcolors.name_to_rgb(color_name.lower(), spec='html4')
            return {"r": rgb.red, "g": rgb.green, "b": rgb.blue}
        except ValueError:
            return None'''

# Replace the function
if old_function in content:
    content = content.replace(old_function, new_function)
    print("[OK] Successfully patched lookup_color_by_name function")

    # Write back to file
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] File saved successfully")
    print("\nPigment code support has been added!")
    print("The lookup_color_by_name function now supports pigment codes like 'PY 43'")
else:
    print("[FAIL] Could not find the function to patch")
    print("Make sure app.py is in the current directory")
