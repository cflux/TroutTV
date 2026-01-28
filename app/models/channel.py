from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PlaylistItem(BaseModel):
    file_path: str
    duration: int  # Duration in seconds
    title: str
    description: Optional[str] = ""


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
    playlist: List[PlaylistItem] = Field(default_factory=list)
    loop: bool = True
    start_time: Optional[datetime] = None  # ISO format, None means continuous from epoch
    stream_settings: StreamSettings = Field(default_factory=StreamSettings)
    enabled: bool = True
