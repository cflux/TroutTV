import json
import uuid
from pathlib import Path
from typing import List, Optional
from app.models.playlist import Playlist
from app.config import settings


class PlaylistManager:
    def __init__(self):
        self.playlists_dir = settings.playlists_dir

    def list_playlists(self) -> List[Playlist]:
        """List all playlists from JSON files."""
        playlists = []
        for json_file in self.playlists_dir.glob("*.json"):
            # Skip migration log file
            if json_file.name.startswith("_"):
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    playlist = Playlist(**data)
                    playlists.append(playlist)
            except Exception as e:
                print(f"Error loading playlist {json_file}: {e}")

        # Sort by name
        playlists.sort(key=lambda x: x.name.lower())
        return playlists

    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """Get a specific playlist by ID."""
        json_file = self.playlists_dir / f"{playlist_id}.json"
        if not json_file.exists():
            return None

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Playlist(**data)
        except Exception as e:
            print(f"Error loading playlist {playlist_id}: {e}")
            return None

    def create_playlist(self, playlist: Playlist) -> Playlist:
        """Create a new playlist."""
        # Generate ID if not provided
        if not playlist.id:
            playlist.id = str(uuid.uuid4())

        # Save to file
        json_file = self.playlists_dir / f"{playlist.id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(playlist.model_dump(mode='json'), f, indent=2, default=str)

        return playlist

    def update_playlist(self, playlist_id: str, playlist: Playlist) -> Optional[Playlist]:
        """Update an existing playlist."""
        json_file = self.playlists_dir / f"{playlist_id}.json"
        if not json_file.exists():
            return None

        # Ensure ID matches
        playlist.id = playlist_id

        # Update timestamp
        from datetime import datetime
        playlist.updated_at = datetime.utcnow()

        # Save to file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(playlist.model_dump(mode='json'), f, indent=2, default=str)

        return playlist

    def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist."""
        json_file = self.playlists_dir / f"{playlist_id}.json"
        if not json_file.exists():
            return False

        json_file.unlink()
        return True

    def is_playlist_in_use(self, playlist_id: str) -> bool:
        """Check if any channel references this playlist."""
        from app.services.channel_manager import channel_manager

        channels = channel_manager.list_channels()
        for channel in channels:
            # Check both playlist_id and scheduled_playlists
            if channel.playlist_id == playlist_id:
                return True
            for scheduled in channel.scheduled_playlists:
                if scheduled.playlist_id == playlist_id:
                    return True

        return False


# Global instance
playlist_manager = PlaylistManager()
