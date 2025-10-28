#!/usr/bin/env python3
"""
Patch script to enhance the upload_drawing endpoint with EXIF extraction.
"""

# Read the app.py file
with open("app.py", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Define the old function
old_function = '''@app.post("/api/drawings/upload")
async def upload_drawing(
    file: UploadFile = File(...),
    comment: Optional[str] = None
):
    """Upload a new drawing for critique"""
    try:
        # Generate unique ID for drawing
        drawing_id = str(int(datetime.now().timestamp() * 1000))

        # Save the file
        file_extension = Path(file.filename).suffix
        filename = f"{drawing_id}{file_extension}"
        file_path = UPLOADS_DIR / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load drawings database
        drawings = json.loads(DRAWINGS_FILE.read_text())

        # Create drawing record
        new_drawing = {
            "id": drawing_id,
            "filename": filename,
            "path": str(file_path),
            "originalName": file.filename,
            "comment": comment or "",
            "uploadedAt": datetime.now().isoformat(),
            "critique": None
        }

        drawings.append(new_drawing)
        DRAWINGS_FILE.write_text(json.dumps(drawings, indent=2))

        logger.info(f"Drawing uploaded: {drawing_id}")
        return {"success": True, "drawing": new_drawing}

    except Exception as e:
        logger.error(f"Error uploading drawing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))'''

# Define the new function with EXIF extraction
new_function = '''@app.post("/api/drawings/upload")
async def upload_drawing(
    file: UploadFile = File(...),
    comment: Optional[str] = None
):
    """Upload a new drawing for critique"""
    try:
        from exif_extractor import get_metadata_with_fallback

        # Generate unique ID for drawing
        drawing_id = str(int(datetime.now().timestamp() * 1000))

        # Save the file
        file_extension = Path(file.filename).suffix
        filename = f"{drawing_id}{file_extension}"
        file_path = UPLOADS_DIR / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract EXIF metadata from the image
        exif_data = get_metadata_with_fallback(str(file_path))

        # Load drawings database
        drawings = json.loads(DRAWINGS_FILE.read_text())

        # Create drawing record with EXIF data
        new_drawing = {
            "id": drawing_id,
            "filename": filename,
            "path": str(file_path),
            "originalName": file.filename,
            "comment": comment or "",
            "uploadedAt": datetime.now().isoformat(),
            "critique": None,
            "exifData": exif_data
        }

        drawings.append(new_drawing)
        DRAWINGS_FILE.write_text(json.dumps(drawings, indent=2))

        # Also store in metadata.json for artwork
        metadata = json.loads(METADATA_FILE.read_text())
        if "artwork" not in metadata:
            metadata["artwork"] = {}

        metadata["artwork"][str(file_path)] = {
            "exifData": exif_data,
            "uploadedAt": datetime.now().isoformat(),
            "originalName": file.filename
        }

        METADATA_FILE.write_text(json.dumps(metadata, indent=2))

        logger.info(f"Drawing uploaded: {drawing_id} with EXIF data: {exif_data}")
        return {"success": True, "drawing": new_drawing}

    except Exception as e:
        logger.error(f"Error uploading drawing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))'''

# Replace the function
if old_function in content:
    content = content.replace(old_function, new_function)
    print("[OK] Successfully patched upload_drawing function with EXIF extraction")

    # Write back to file
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] File saved successfully")
    print("\nEXIF extraction has been added to the upload endpoint!")
    print("Artwork uploads will now extract and store date/year information")
else:
    print("[FAIL] Could not find the upload_drawing function to patch")
    print("Make sure app.py is in the current directory")
