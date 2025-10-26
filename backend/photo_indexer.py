#!/usr/bin/env python3
"""
Photo Indexer - Scans photos and creates a comprehensive JSON index with AI-powered metadata.
Uses Hugging Face models to analyze image content and generate metadata suggestions.

Usage:
    python photo_indexer.py                 # Index all photo collections
    python photo_indexer.py --collection my-photos     # Index specific collection
    python photo_indexer.py --single /path/to/image.jpg # Index single image
"""

import json
import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from PIL import Image
import torch
from transformers import (
    pipeline,
    AutoImageProcessor,
    AutoModelForImageClassification,
    CLIPProcessor,
    CLIPModel
)
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = Path(__file__).parent

# Status file for progress reporting
STATUS_FILE = BACKEND_DIR / "data" / "indexer_status.json"

# Load config
def load_config():
    """Load image paths from config.json"""
    config_file = BACKEND_DIR / "config.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            paths = config.get("image_paths", {})
            fallback = config.get("fallback_paths", {})

            result = {}

            # Check reference paths
            ref_paths = paths.get("reference", [])
            valid_ref_paths = [p for p in ref_paths if Path(p).exists()]
            if valid_ref_paths:
                result["reference"] = valid_ref_paths
            else:
                fallback_refs = fallback.get("reference", [])
                result["reference"] = [str(PROJECT_ROOT / p) if not Path(p).is_absolute() else p
                                      for p in fallback_refs]

            # Check photos path
            photos_path = paths.get("photos", "")
            if photos_path and Path(photos_path).exists():
                result["photos"] = photos_path
            else:
                fallback_photos = fallback.get("photos", "./sample_images/photos")
                result["photos"] = str(PROJECT_ROOT / fallback_photos) if not Path(fallback_photos).is_absolute() else fallback_photos

            # Check artwork path
            artwork_path = paths.get("artwork", "")
            if artwork_path and Path(artwork_path).exists():
                result["artwork"] = artwork_path
            else:
                fallback_artwork = fallback.get("artwork", "./sample_images/artwork")
                result["artwork"] = str(PROJECT_ROOT / fallback_artwork) if not Path(fallback_artwork).is_absolute() else fallback_artwork

            return result
        except Exception as e:
            logger.warning(f"Error loading config.json: {e}, using fallback paths")

    # Default fallback
    return {
        "reference": [str(PROJECT_ROOT / "sample_images" / "reference")],
        "photos": str(PROJECT_ROOT / "sample_images" / "photos"),
        "artwork": str(PROJECT_ROOT / "sample_images" / "artwork")
    }

IMAGE_PATHS = load_config()
DATA_DIR = BACKEND_DIR / "data"
PHOTO_INDEX_FILE = DATA_DIR / "photo_index.json"

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

class ImageAnalyzer:
    """Analyzes images and extracts metadata using Hugging Face models"""

    def __init__(self):
        """Initialize the image analysis models"""
        logger.info("Initializing image analysis models...")

        # Object detection/image classification - for subject type detection
        self.classifier = pipeline(
            "image-classification",
            model="google/vit-base-patch16-224",
            device=0 if torch.cuda.is_available() else -1
        )

        # Zero-shot classification for specific attributes
        self.zero_shot = pipeline(
            "zero-shot-image-classification",
            model="openai/clip-vit-base-patch32",
            device=0 if torch.cuda.is_available() else -1
        )

        logger.info("Models loaded successfully")

    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze an image and return metadata suggestions

        Returns:
            Dict with keys: subject_type, gender, lighting, skills
        """
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return self._default_metadata()

        metadata = {
            "subject_type": self._detect_subject_type(image),
            "gender": self._detect_gender(image),
            "lighting": self._detect_lighting(image),
            "skills": self._suggest_skills(image)
        }

        return metadata

    def _detect_subject_type(self, image: Image.Image) -> str:
        """Detect the primary subject type in the image"""
        try:
            candidates = ["person", "people", "animal", "building", "landscape", "still life", "object"]
            results = self.zero_shot(candidate_labels=candidates, images=image)

            # Extract the top result label
            label = ""

            # Handle different result formats from zero-shot pipeline
            if isinstance(results, list) and len(results) > 0:
                # Most common: list of dicts with 'label' and 'score' keys
                first_result = results[0]
                if isinstance(first_result, dict):
                    label = first_result.get('label', '').lower()
                elif isinstance(first_result, str):
                    label = first_result.lower()
            elif isinstance(results, dict):
                # Alternative format: dict with 'labels' and 'scores' keys
                labels = results.get('labels', [])
                if labels:
                    # Handle if labels is a list of strings or dicts
                    if isinstance(labels, list) and len(labels) > 0:
                        first_label = labels[0]
                        if isinstance(first_label, str):
                            label = first_label.lower()
                        elif isinstance(first_label, dict):
                            label = first_label.get('label', '').lower()

            if label:
                if 'person' in label or 'people' in label:
                    return "People"
                elif 'animal' in label:
                    return "Animals"
                elif 'building' in label or 'architecture' in label:
                    return "Buildings"
                elif 'landscape' in label or 'outdoor' in label or 'nature' in label:
                    return "Landscapes"

            return "All"
        except Exception as e:
            logger.warning(f"Error detecting subject type: {e}")
            return "All"

    def _detect_gender(self, image: Image.Image) -> str:
        """Detect if image contains people and estimate gender representation"""
        try:
            candidates = ["female person", "male person", "no people", "mixed"]
            results = self.zero_shot(candidate_labels=candidates, images=image)

            # Extract the top result label
            label = ""

            # Handle different result formats from zero-shot pipeline
            if isinstance(results, list) and len(results) > 0:
                # Most common: list of dicts with 'label' and 'score' keys
                first_result = results[0]
                if isinstance(first_result, dict):
                    label = first_result.get('label', '').lower()
                elif isinstance(first_result, str):
                    label = first_result.lower()
            elif isinstance(results, dict):
                # Alternative format: dict with 'labels' and 'scores' keys
                labels = results.get('labels', [])
                if labels:
                    # Handle if labels is a list of strings or dicts
                    if isinstance(labels, list) and len(labels) > 0:
                        first_label = labels[0]
                        if isinstance(first_label, str):
                            label = first_label.lower()
                        elif isinstance(first_label, dict):
                            label = first_label.get('label', '').lower()

            if label:
                if 'female' in label:
                    return "Female"
                elif 'male' in label:
                    return "Male"

            return "All"
        except Exception as e:
            logger.warning(f"Error detecting gender: {e}")
            return "All"

    def _detect_lighting(self, image: Image.Image) -> str:
        """Analyze image lighting conditions"""
        try:
            # Analyze image brightness and contrast
            img_array = np.array(image)
            brightness = np.mean(img_array)

            # Calculate contrast
            gray = np.mean(img_array, axis=2)
            contrast = np.std(gray)

            # Detect saturation for colorfulness
            hsv_array = np.array(image.convert('HSV'))
            saturation = np.mean(hsv_array[:, :, 1])

            # Classify lighting
            if saturation > 150:
                return "Colorful"
            elif brightness > 200:
                return "Bright"
            elif brightness < 100:
                return "Dark"
            elif contrast > 50:
                return "High Contrast"
            else:
                return "All"

        except Exception as e:
            logger.warning(f"Error detecting lighting: {e}")
            return "All"

    def _suggest_skills(self, image: Image.Image) -> List[str]:
        """Suggest relevant art skills for this image"""
        skills = []

        try:
            # Detect features that match skills
            candidates = [
                "perspective", "foreshortening", "drapery", "proportion",
                "anatomy", "gesture", "composition", "value", "color harmony",
                "light and shadow", "texture", "form", "balance"
            ]

            results = self.zero_shot(candidate_labels=candidates, images=image)

            # Handle different result formats from zero-shot pipeline
            if isinstance(results, list) and len(results) > 0:
                # Most common: list of dicts with 'label' and 'score' keys
                for result in results[:4]:
                    if isinstance(result, dict):
                        score = result.get('score', 0)
                        label = result.get('label', '')
                        if isinstance(score, (int, float)) and score > 0.1:
                            skills.append(label.title() if isinstance(label, str) else str(label).title())
            elif isinstance(results, dict):
                # Alternative format: dict with 'labels' and 'scores' keys
                labels = results.get('labels', [])
                scores = results.get('scores', [])
                if labels and scores:
                    for label, score in zip(labels[:4], scores[:4]):
                        if isinstance(score, (int, float)) and score > 0.1:
                            if isinstance(label, str):
                                skills.append(label.title())
                            elif isinstance(label, dict):
                                skills.append(label.get('label', '').title())

            # Also add skills based on subject type
            subject_type = self._detect_subject_type(image)
            if subject_type == "People":
                if "Anatomy" not in skills:
                    skills.insert(0, "Anatomy")
                if "Proportion" not in skills:
                    skills.append("Proportion")
            elif subject_type == "Landscapes":
                if "Perspective" not in skills:
                    skills.insert(0, "Perspective")

            # Ensure we have at least one skill
            if not skills:
                skills = ["Composition"]

            return skills[:4]  # Limit to 4 skills

        except Exception as e:
            logger.warning(f"Error suggesting skills: {e}")
            return ["Composition"]

    def _default_metadata(self) -> Dict:
        """Return default metadata when analysis fails"""
        return {
            "subject_type": "All",
            "gender": "All",
            "lighting": "All",
            "skills": ["Composition"]
        }


class PhotoIndexer:
    """Manages photo indexing and index file generation"""

    def __init__(self):
        self.analyzer = ImageAnalyzer()
        self.index = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            },
            "collections": {}
        }

    def write_status(self, collection_name: str, current: int, total: int, current_image: str = None) -> None:
        """Write progress status to a JSON file for frontend monitoring"""
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        status = {
            "isRunning": True,
            "collection": collection_name,
            "current": current,
            "total": total,
            "percentage": round((current / total * 100)) if total > 0 else 0,
            "currentImage": current_image or "",
            "updatedAt": datetime.now().isoformat()
        }
        try:
            STATUS_FILE.write_text(json.dumps(status, indent=2))
        except Exception as e:
            logger.error(f"Failed to write status: {e}")

    def write_completion_status(self) -> None:
        """Write completion status when indexing finishes"""
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        status = {
            "isRunning": False,
            "collection": None,
            "current": 0,
            "total": 0,
            "percentage": 100,
            "currentImage": None,
            "updatedAt": datetime.now().isoformat(),
            "completedAt": datetime.now().isoformat()
        }
        try:
            STATUS_FILE.write_text(json.dumps(status, indent=2))
        except Exception as e:
            logger.error(f"Failed to write completion status: {e}")

    def record_execution_time(self, duration_seconds: float) -> None:
        """Record the execution time to history file for tracking and prediction"""
        history_file = DATA_DIR / "indexer_history.json"

        try:
            # Load existing history
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = {"executions": []}

            # Add new execution record
            history["executions"].append({
                "completedAt": datetime.now().isoformat(),
                "durationSeconds": round(duration_seconds, 2),
                "durationMinutes": round(duration_seconds / 60, 2),
                "durationFormatted": self._format_duration(duration_seconds)
            })

            # Keep only last 5 executions
            history["executions"] = history["executions"][-5:]

            # Calculate average time
            if history["executions"]:
                avg_seconds = sum(e["durationSeconds"] for e in history["executions"]) / len(history["executions"])
                history["averageDurationSeconds"] = round(avg_seconds, 2)
                history["averageDurationMinutes"] = round(avg_seconds / 60, 2)
                history["averageDurationFormatted"] = self._format_duration(avg_seconds)

            # Write back to file
            history_file.write_text(json.dumps(history, indent=2))
            logger.info(f"Execution time recorded: {self._format_duration(duration_seconds)}")
        except Exception as e:
            logger.error(f"Failed to record execution time: {e}")

    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable string"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def scan_directory(self, directory: str, collection_name: str) -> None:
        """Scan a directory and add all images to the index"""
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.warning(f"Directory not found: {directory}")
            return

        logger.info(f"Scanning collection '{collection_name}': {directory}")

        image_files = []
        for ext in IMAGE_EXTENSIONS:
            image_files.extend(dir_path.rglob(f"*{ext}"))

        logger.info(f"Found {len(image_files)} images in {collection_name}")

        if len(image_files) == 0:
            logger.warning(f"No images found in {directory}")
            self.index["collections"][collection_name] = {}
            return

        collection_index = {}

        for idx, image_path in enumerate(image_files, 1):
            relative_path = str(image_path.relative_to(dir_path))
            logger.info(f"[{idx}/{len(image_files)}] Analyzing: {relative_path}")

            # Write progress status
            self.write_status(collection_name, idx, len(image_files), relative_path)

            try:
                metadata = self.analyzer.analyze_image(str(image_path))
                collection_index[relative_path] = metadata
            except Exception as e:
                logger.error(f"Error analyzing {relative_path}: {e}")
                collection_index[relative_path] = self.analyzer._default_metadata()

        self.index["collections"][collection_name] = collection_index
        logger.info(f"Completed indexing {collection_name}")

        # Save index incrementally so search results update while indexing
        self.save_index()
        logger.info(f"Index saved incrementally for {collection_name}")

    def index_single_image(self, image_path: str, collection_name: str = "single_images") -> None:
        """Index a single image"""
        path = Path(image_path)

        if not path.exists():
            logger.error(f"Image not found: {image_path}")
            return

        logger.info(f"Analyzing single image: {image_path}")

        try:
            metadata = self.analyzer.analyze_image(image_path)

            if collection_name not in self.index["collections"]:
                self.index["collections"][collection_name] = {}

            self.index["collections"][collection_name][image_path] = metadata
            logger.info(f"Completed indexing single image")
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")

    def index_all_collections(self) -> None:
        """Index all photo collections"""
        collections = {
            "My Photos": IMAGE_PATHS.get("photos"),
            "Reference Photos": IMAGE_PATHS.get("reference", [None])[0],
            "My Art": IMAGE_PATHS.get("artwork")
        }

        for collection_name, directory in collections.items():
            if directory and Path(directory).exists():
                self.scan_directory(directory, collection_name)

    def save_index(self) -> None:
        """Save the index to JSON file"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        with open(PHOTO_INDEX_FILE, 'w') as f:
            json.dump(self.index, f, indent=2)

        logger.info(f"Index saved to: {PHOTO_INDEX_FILE}")
        logger.info(f"Total collections: {len(self.index['collections'])}")

        for collection, images in self.index['collections'].items():
            logger.info(f"  {collection}: {len(images)} images")


def main():
    parser = argparse.ArgumentParser(
        description="Photo Indexer - Scans photos and creates a comprehensive JSON index"
    )

    parser.add_argument(
        '--collection',
        help='Index a specific collection (my-photos, reference-photos, my-art)',
        choices=['my-photos', 'reference-photos', 'my-art'],
        default=None
    )

    parser.add_argument(
        '--single',
        help='Index a single image file',
        default=None
    )

    parser.add_argument(
        '--output',
        help='Output file path (default: backend/data/photo_index.json)',
        default=str(PHOTO_INDEX_FILE)
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Photo Indexer - Hugging Face powered image analysis")
    logger.info("=" * 60)

    # Record start time
    start_time = datetime.now()
    logger.info(f"Indexing started at {start_time.isoformat()}")

    indexer = PhotoIndexer()

    if args.single:
        # Index single image
        indexer.index_single_image(args.single)
    elif args.collection:
        # Index specific collection
        collections_map = {
            'my-photos': ('My Photos', IMAGE_PATHS.get("photos")),
            'reference-photos': ('Reference Photos', IMAGE_PATHS.get("reference", [None])[0]),
            'my-art': ('My Art', IMAGE_PATHS.get("artwork"))
        }

        collection_name, directory = collections_map[args.collection]
        if directory:
            indexer.scan_directory(directory, collection_name)
        else:
            logger.error(f"Collection directory not found: {args.collection}")
            sys.exit(1)
    else:
        # Index all collections
        indexer.index_all_collections()

    indexer.save_index()
    indexer.write_completion_status()

    # Record execution time
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    indexer.record_execution_time(duration)

    logger.info("=" * 60)
    logger.info("Indexing complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
