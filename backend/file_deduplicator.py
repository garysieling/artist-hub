"""
File deduplication utility using SHA256 hash.
Detects duplicate files and maintains a registry of file hashes.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# File hash registry - stores filename -> sha256 hash
HASH_REGISTRY_FILE = Path(__file__).parent / "data" / "file_hashes.json"


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate the hash of a file using the specified algorithm.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hex string of the file hash
    """
    hash_obj = hashlib.new(algorithm)

    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        return ""


def load_hash_registry() -> Dict[str, str]:
    """
    Load the file hash registry from disk.

    Returns:
        Dictionary mapping file hashes to original filenames
    """
    if HASH_REGISTRY_FILE.exists():
        try:
            return json.loads(HASH_REGISTRY_FILE.read_text())
        except Exception as e:
            logger.warning(f"Error loading hash registry: {e}")
            return {}
    return {}


def save_hash_registry(registry: Dict[str, str]) -> None:
    """
    Save the file hash registry to disk.

    Args:
        registry: Dictionary mapping file hashes to filenames
    """
    try:
        HASH_REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HASH_REGISTRY_FILE.write_text(json.dumps(registry, indent=2))
    except Exception as e:
        logger.error(f"Error saving hash registry: {e}")


def is_file_duplicate(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a file is a duplicate based on its hash.

    Args:
        file_path: Path to the file to check

    Returns:
        Tuple of (is_duplicate, original_filename)
        - is_duplicate: True if file hash already exists in registry
        - original_filename: The original filename if duplicate, None otherwise
    """
    file_hash = calculate_file_hash(file_path)

    if not file_hash:
        return False, None

    registry = load_hash_registry()

    if file_hash in registry:
        logger.info(f"Duplicate detected: {Path(file_path).name} matches {registry[file_hash]}")
        return True, registry[file_hash]

    return False, None


def register_file(file_path: str) -> str:
    """
    Register a file in the hash registry.

    Args:
        file_path: Path to the file

    Returns:
        The file hash
    """
    file_hash = calculate_file_hash(file_path)

    if file_hash:
        registry = load_hash_registry()
        filename = Path(file_path).name
        registry[file_hash] = filename
        save_hash_registry(registry)
        logger.debug(f"Registered file: {filename} with hash {file_hash[:16]}...")

    return file_hash


def check_and_register(file_path: str) -> Tuple[bool, Optional[str], str]:
    """
    Check if a file is a duplicate and register it if it's not.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (is_duplicate, original_filename, file_hash)
        - is_duplicate: True if file is a duplicate
        - original_filename: The original filename if duplicate
        - file_hash: The file hash
    """
    is_dup, original = is_file_duplicate(file_path)

    if not is_dup:
        file_hash = register_file(file_path)
    else:
        file_hash = calculate_file_hash(file_path)

    return is_dup, original, file_hash


def get_registry_stats() -> Dict[str, int]:
    """
    Get statistics about the file hash registry.

    Returns:
        Dictionary with registry statistics
    """
    registry = load_hash_registry()
    return {
        "total_files_tracked": len(registry),
        "registry_size_bytes": HASH_REGISTRY_FILE.stat().st_size if HASH_REGISTRY_FILE.exists() else 0
    }
