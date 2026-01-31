"""Media directory scanning service for browsing and metadata extraction."""
from pathlib import Path
from typing import Optional, Dict, List
import subprocess
import json
from datetime import datetime
from fastapi import HTTPException
from app.config import settings


def validate_path(user_path: str, base_dir: Path) -> Path:
    """
    Validate that the requested path is within the base directory.
    Prevents directory traversal attacks.

    Args:
        user_path: User-provided path (relative or absolute)
        base_dir: Base directory to restrict access to

    Returns:
        Resolved path if valid

    Raises:
        HTTPException: If path is invalid or outside base directory
    """
    if not user_path:
        return base_dir

    # Reject absolute paths and drive letters on Windows
    if Path(user_path).is_absolute():
        raise HTTPException(status_code=400, detail="Absolute paths are not allowed")

    # Reject paths with parent directory references
    if '..' in user_path:
        raise HTTPException(status_code=400, detail="Parent directory references are not allowed")

    # Construct the full path
    requested_path = (base_dir / user_path).resolve()
    base_resolved = base_dir.resolve()

    # Ensure the resolved path is within the base directory
    try:
        requested_path.relative_to(base_resolved)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path: outside allowed directory")

    # Check if path exists
    if not requested_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    return requested_path


def is_allowed_media_file(filename: str) -> bool:
    """
    Check if a filename has an allowed media extension.

    Args:
        filename: Name of the file to check

    Returns:
        True if file has allowed extension, False otherwise
    """
    ext = Path(filename).suffix.lower()
    return ext in settings.allowed_media_extensions


def get_video_duration(file_path: Path) -> Optional[int]:
    """
    Extract video duration using ffprobe.

    Args:
        file_path: Path to the video file

    Returns:
        Duration in seconds, or None if extraction fails
    """
    try:
        result = subprocess.run(
            [
                settings.ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = data.get('format', {}).get('duration')
            if duration:
                return int(float(duration))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError, FileNotFoundError):
        pass

    return None


def scan_directory(path: Path, media_dir: Path) -> Dict:
    """
    Scan a directory and return file/folder listing with metadata.

    Args:
        path: Directory path to scan
        media_dir: Base media directory (for calculating relative paths)

    Returns:
        Dictionary with current_path, parent_path, and items list
    """
    if not path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")

    # Calculate relative paths
    try:
        current_relative = str(path.relative_to(media_dir)).replace('\\', '/')
        if current_relative == '.':
            current_relative = ''
    except ValueError:
        current_relative = ''

    # Calculate parent path
    parent_path = None
    if path != media_dir:
        parent = path.parent
        try:
            parent_relative = str(parent.relative_to(media_dir)).replace('\\', '/')
            parent_path = parent_relative if parent_relative != '.' else ''
        except ValueError:
            parent_path = ''

    # Scan directory
    items: List[Dict] = []

    try:
        for entry in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            # Skip hidden files
            if entry.name.startswith('.'):
                continue

            if entry.is_dir():
                # Directory entry
                item_relative = str(entry.relative_to(media_dir)).replace('\\', '/')
                items.append({
                    'name': entry.name,
                    'type': 'directory',
                    'path': item_relative,
                    'modified': datetime.fromtimestamp(entry.stat().st_mtime).isoformat()
                })
            elif entry.is_file() and is_allowed_media_file(entry.name):
                # Media file entry
                item_relative = str(entry.relative_to(media_dir)).replace('\\', '/')
                stat = entry.stat()

                item = {
                    'name': entry.name,
                    'type': 'file',
                    'path': item_relative,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }

                # Try to get video duration
                duration = get_video_duration(entry)
                if duration:
                    item['duration'] = duration

                items.append(item)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    return {
        'current_path': current_relative,
        'parent_path': parent_path,
        'items': items
    }
