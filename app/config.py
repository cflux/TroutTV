from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    base_url: str = "http://localhost:8000"

    # Directory paths
    channels_dir: Path = Path("D:/claude/TroutTV/data/channels")
    media_dir: Path = Path("D:/claude/TroutTV/data/media")
    logos_dir: Path = Path("D:/claude/TroutTV/data/logos")
    streams_dir: Path = Path("D:/claude/TroutTV/streams")

    # Stream settings
    stream_timeout: int = 60  # Seconds of inactivity before stopping stream
    cleanup_interval: int = 30  # Seconds between cleanup task runs

    # FFmpeg settings
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"

    # EPG settings
    epg_days_ahead: int = 2

    # File upload settings
    allowed_logo_extensions: list[str] = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']
    max_logo_size_mb: int = 5
    allowed_media_extensions: list[str] = ['.mp4', '.mkv', '.avi', '.mov', '.ts', '.m4v']

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.channels_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.logos_dir.mkdir(parents=True, exist_ok=True)
        self.streams_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
