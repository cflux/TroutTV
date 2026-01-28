from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StreamStatus(BaseModel):
    channel_id: str
    is_active: bool
    current_file: Optional[str] = None
    current_title: Optional[str] = None
    seek_position: Optional[float] = None
    last_request: Optional[datetime] = None
    viewer_count: int = 0  # Future enhancement
