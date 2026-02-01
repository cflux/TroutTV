from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.playlist import PlaylistItem


class ScheduledPlaylist(BaseModel):
    """Future: Allow multiple playlists with scheduling rules."""
    playlist_id: str
    day_of_week: Optional[List[int]] = None  # 0-6 (Monday-Sunday), None = all days
    start_time: Optional[str] = None  # HH:MM format
    end_time: Optional[str] = None    # HH:MM format
    priority: int = 0  # Higher priority wins if multiple match


class StreamSettings(BaseModel):
    video_bitrate: int = 3000  # kbps
    audio_bitrate: int = 128  # kbps
    segment_duration: int = 6  # seconds
    playlist_size: int = 10  # number of segments to keep
    transcode_preset: str = "software_fast"  # software_fast, software_medium, qsv, nvenc
    resolution: str = "1280x720"  # WxH


class Channel(BaseModel):
    id: str
    name: str
    number: int
    category: str = "General"
    logo_url: Optional[str] = None

    # Phase 1: Single playlist reference
    playlist_id: Optional[str] = None

    # Keep for backward compatibility during migration
    playlist: List[PlaylistItem] = Field(default_factory=list)

    # Phase 2: Multiple scheduled playlists (future)
    scheduled_playlists: List[ScheduledPlaylist] = Field(default_factory=list)

    loop: bool = True
    start_time: Optional[datetime] = None  # ISO format, None means continuous from epoch
    stream_settings: StreamSettings = Field(default_factory=StreamSettings)
    enabled: bool = True
