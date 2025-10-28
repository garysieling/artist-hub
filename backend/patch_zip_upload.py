#!/usr/bin/env python3
"""
Patch script to add ZIP file upload support with deduplication to the upload endpoint.
"""

# Read the app.py file
with open("app.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# Find the upload_drawing function and add a new ZIP upload endpoint right after it
# We'll add this new endpoint after the upload_drawing function

# First, find where to insert the new function
insert_index = None
for i, line in enumerate(lines):
    if '@app.get("/api/drawings")' in line:
        insert_index = i
        break

if insert_index is None:
    print("[FAIL] Could not find insertion point in app.py")
else:
    # Create the new ZIP upload endpoint
    zip_upload_endpoint = '''@app.post("/api/drawings/upload-zip")
async def upload_drawings_from_zip(
    file: UploadFile = File(...),
    comment: Optional[str] = None
):
    """Upload multiple drawings from a ZIP file with duplicate detection"""
    try:
        from exif_extractor import get_metadata_with_fallback
        from file_deduplicator import check_and_register
        import io

        if not file.filename.lower().endswith('.zip'):
            raise HTTPException(status_code=400, detail="File must be a ZIP archive")

        # Create a temporary directory for extraction
        temp_dir = Path(tempfile.mkdtemp())
        zip_path = temp_dir / file.filename

        # Save the ZIP file temporarily
        with zip_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract ZIP file
        uploaded_drawings = []
        skipped_drawings = []

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                # Skip directories and non-image files
                if file_info.is_dir():
                    continue

                filename_lower = file_info.filename.lower()
                if not any(filename_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                    continue

                # Extract file to temporary location
                temp_file_path = temp_dir / file_info.filename

                # Create subdirectories if needed
                temp_file_path.parent.mkdir(parents=True, exist_ok=True)

                # Extract the file
                with zip_ref.open(file_info) as source, temp_file_path.open("wb") as target:
                    shutil.copyfileobj(source, target)

                # Check for duplicates using file hash
                is_duplicate, original_filename, file_hash = check_and_register(str(temp_file_path))

                if is_duplicate:
                    logger.info(f"Skipping duplicate: {file_info.filename} (matches {original_filename})")
                    skipped_drawings.append({
                        "filename": file_info.filename,
                        "reason": "duplicate",
                        "original": original_filename,
                        "hash": file_hash
                    })
                    continue

                # Process the file
                drawing_id = str(int(datetime.now().timestamp() * 1000))

                # Save the file to uploads directory
                file_extension = Path(file_info.filename).suffix
                filename = f"{drawing_id}{file_extension}"
                file_path = UPLOADS_DIR / filename

                # Copy from temp location to uploads directory
                shutil.copy2(str(temp_file_path), str(file_path))

                # Extract EXIF metadata
                exif_data = get_metadata_with_fallback(str(file_path))

                # Load drawings database
                drawings = json.loads(DRAWINGS_FILE.read_text())

                # Create drawing record
                new_drawing = {
                    "id": drawing_id,
                    "filename": filename,
                    "path": str(file_path),
                    "originalName": file_info.filename,
                    "comment": comment or "",
                    "uploadedAt": datetime.now().isoformat(),
                    "critique": None,
                    "exifData": exif_data
                }

                drawings.append(new_drawing)
                DRAWINGS_FILE.write_text(json.dumps(drawings, indent=2))

                # Store in metadata.json
                metadata = json.loads(METADATA_FILE.read_text())
                if "artwork" not in metadata:
                    metadata["artwork"] = {}

                metadata["artwork"][str(file_path)] = {
                    "exifData": exif_data,
                    "uploadedAt": datetime.now().isoformat(),
                    "originalName": file_info.filename,
                    "fileHash": file_hash
                }

                METADATA_FILE.write_text(json.dumps(metadata, indent=2))

                uploaded_drawings.append(new_drawing)
                logger.info(f"Drawing uploaded from ZIP: {drawing_id}")

        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

        return {
            "success": True,
            "uploaded": len(uploaded_drawings),
            "skipped": len(skipped_drawings),
            "drawings": uploaded_drawings,
            "skipped_details": skipped_drawings
        }

    except Exception as e:
        logger.error(f"Error uploading drawings from ZIP: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

'''

    # Insert the new endpoint
    lines.insert(insert_index, zip_upload_endpoint + '\n')

    # Write back to file
    with open("app.py", "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("[OK] Successfully added ZIP upload endpoint to app.py")
    print("[OK] File saved successfully")
    print("\nZIP file upload with deduplication has been added!")
    print("Endpoint: POST /api/drawings/upload-zip")
    print("Features:")
    print("  - Extract multiple images from ZIP files")
    print("  - Automatic duplicate detection using SHA256 hashing")
    print("  - EXIF metadata extraction for each image")
    print("  - Skips duplicate files (e.g., from Google Photos)")
