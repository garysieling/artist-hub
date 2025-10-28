"""
EXIF metadata extraction utility for images.
Extracts datetime, camera info, and other metadata from image files.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import logging

logger = logging.getLogger(__name__)


def extract_exif_data(image_path: str) -> Dict[str, Any]:
    """
    Extract EXIF metadata from an image file.

    Args:
        image_path: Path to the image file (JPG, PNG, etc.)

    Returns:
        Dictionary with extracted EXIF data including:
        - year: Extracted year from EXIF DateTimeOriginal or DateTime
        - dateTime: Full datetime string if available
        - camera: Camera model
        - make: Camera manufacturer
        - software: Software used
        - hasExif: Whether EXIF data was found
    """

    exif_data = {
        "year": None,
        "dateTime": None,
        "camera": None,
        "make": None,
        "software": None,
        "hasExif": False
    }

    try:
        image = Image.open(image_path)

        # Try to get EXIF data
        exif = image.getexif()

        if not exif:
            logger.debug(f"No EXIF data found in {image_path}")
            return exif_data

        exif_data["hasExif"] = True

        # Try to extract datetime (most important for sorting)
        # Try multiple datetime fields in order of preference
        datetime_str = None
        for tag_id in [36867, 306, 36868]:  # DateTimeOriginal, DateTime, DateTimeDigitized
            if tag_id in exif:
                datetime_str = exif[tag_id]
                break

        if datetime_str:
            exif_data["dateTime"] = datetime_str
            # Extract year from datetime string (format: "YYYY:MM:DD HH:MM:SS")
            try:
                year = int(datetime_str.split(':')[0])
                if 1900 <= year <= 2100:  # Sanity check
                    exif_data["year"] = year
            except (ValueError, IndexError):
                logger.debug(f"Could not parse year from datetime: {datetime_str}")

        # Extract camera model
        camera_model = exif.get(271)  # Make
        if camera_model:
            exif_data["make"] = camera_model if isinstance(camera_model, str) else str(camera_model)

        # Extract camera model
        camera_model = exif.get(272)  # Model
        if camera_model:
            exif_data["camera"] = camera_model if isinstance(camera_model, str) else str(camera_model)

        # Extract software
        software = exif.get(305)  # Software
        if software:
            exif_data["software"] = software if isinstance(software, str) else str(software)

        logger.debug(f"Extracted EXIF from {image_path}: {exif_data}")

    except Exception as e:
        logger.warning(f"Error extracting EXIF from {image_path}: {e}")

    return exif_data


def extract_year_from_path(file_path: str) -> Optional[int]:
    """
    Fallback: Try to extract year from filename if EXIF extraction fails.

    Common patterns:
    - 2023_photo.jpg
    - photo_2023.jpg
    - 2023-12-25.jpg

    Args:
        file_path: Path to the image file

    Returns:
        Year if found in filename, None otherwise
    """

    import re

    filename = Path(file_path).stem.lower()

    # Look for 4-digit number that looks like a year (1900-2100)
    matches = re.findall(r'\b(19|20)\d{2}\b', filename)

    if matches:
        try:
            year = int(matches[0] + matches[1]) if len(matches) > 1 else int(matches[0])
            return year
        except (ValueError, IndexError):
            pass

    return None


def get_metadata_with_fallback(image_path: str) -> Dict[str, Any]:
    """
    Extract EXIF data with fallback to filename analysis.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary with extracted metadata
    """

    metadata = extract_exif_data(image_path)

    # If no year found via EXIF, try filename
    if not metadata["year"]:
        year_from_filename = extract_year_from_path(image_path)
        if year_from_filename:
            metadata["year"] = year_from_filename
            logger.debug(f"Extracted year {year_from_filename} from filename: {image_path}")

    return metadata
