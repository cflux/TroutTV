from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.channel import Channel
from app.services.channel_manager import channel_manager

router = APIRouter(prefix="/api/channels", tags=["channels"])


@router.get("", response_model=List[Channel])
async def list_channels():
    """List all channels."""
    return channel_manager.list_channels()


@router.get("/{channel_id}", response_model=Channel)
async def get_channel(channel_id: str):
    """Get a specific channel."""
    channel = channel_manager.get_channel(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_id} not found"
        )
    return channel


@router.post("", response_model=Channel, status_code=status.HTTP_201_CREATED)
async def create_channel(channel: Channel):
    """Create a new channel."""
    return channel_manager.create_channel(channel)


@router.put("/{channel_id}", response_model=Channel)
async def update_channel(channel_id: str, channel: Channel):
    """Update an existing channel."""
    updated_channel = channel_manager.update_channel(channel_id, channel)
    if not updated_channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_id} not found"
        )
    return updated_channel


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(channel_id: str):
    """Delete a channel."""
    if not channel_manager.delete_channel(channel_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_id} not found"
        )
