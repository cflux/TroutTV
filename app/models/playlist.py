from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PlaylistItem(BaseModel):
    file_path: str
    duration: int  # Duration in seconds
    title: str
    description: Optional[str] = ""


class Playlist(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    items: List[PlaylistItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
