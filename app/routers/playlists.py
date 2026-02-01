from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.playlist import Playlist
from app.services.playlist_manager import playlist_manager

router = APIRouter(prefix="/api/playlists", tags=["playlists"])


@router.get("", response_model=List[Playlist])
async def list_playlists():
    """List all playlists."""
    return playlist_manager.list_playlists()


@router.get("/{playlist_id}", response_model=Playlist)
async def get_playlist(playlist_id: str):
    """Get a specific playlist."""
    playlist = playlist_manager.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playlist {playlist_id} not found"
        )
    return playlist


@router.post("", response_model=Playlist, status_code=status.HTTP_201_CREATED)
async def create_playlist(playlist: Playlist):
    """Create a new playlist."""
    try:
        return playlist_manager.create_playlist(playlist)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating playlist: {str(e)}"
        )


@router.put("/{playlist_id}", response_model=Playlist)
async def update_playlist(playlist_id: str, playlist: Playlist):
    """Update an existing playlist."""
    updated_playlist = playlist_manager.update_playlist(playlist_id, playlist)
    if not updated_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playlist {playlist_id} not found"
        )
    return updated_playlist


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(playlist_id: str):
    """Delete a playlist if not in use."""
    # Check if playlist exists
    playlist = playlist_manager.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playlist {playlist_id} not found"
        )

    # Check if playlist is in use
    if playlist_manager.is_playlist_in_use(playlist_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Playlist is in use by one or more channels"
        )

    # Delete playlist
    if not playlist_manager.delete_playlist(playlist_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting playlist"
        )

    return None
