import subprocess
import json
from datetime import datetime, timezone
from typing import Optional, Tuple
from app.models.channel import Channel
from app.config import settings


class PlaylistScheduler:
    def __init__(self):
        self.ffprobe_path = settings.ffprobe_path

    def get_media_duration(self, file_path: str) -> Optional[float]:
        """Get media duration in seconds using FFprobe."""
        try:
            cmd = [
                self.ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data.get('format', {}).get('duration', 0))
                return duration
            return None
        except Exception as e:
            print(f"Error getting duration for {file_path}: {e}")
            return None

    def get_current_media(self, channel: Channel) -> Optional[Tuple[str, float, str]]:
        """
        Calculate which media file should be playing right now and at what position.

        Returns:
            Tuple of (file_path, seek_seconds, title) or None if playlist is empty
        """
        # Resolve playlist items
        from app.services.playlist_manager import playlist_manager

        playlist_items = []
        if channel.playlist_id:
            playlist = playlist_manager.get_playlist(channel.playlist_id)
            if playlist:
                playlist_items = playlist.items
        elif channel.playlist:
            # Fallback to embedded playlist for backward compatibility
            playlist_items = channel.playlist

        if not playlist_items:
            return None

        # Calculate elapsed time since start
        now_utc = datetime.now(timezone.utc)

        if channel.start_time:
            # Start from specific time
            elapsed = (now_utc - channel.start_time.replace(tzinfo=timezone.utc)).total_seconds()
        else:
            # Continuous mode - start from epoch
            elapsed = now_utc.timestamp()

        # If elapsed is negative (start time in future), wait at first item
        if elapsed < 0:
            return (playlist_items[0].file_path, 0, playlist_items[0].title)

        # Calculate total playlist duration
        total_duration = sum(item.duration for item in playlist_items)

        if total_duration == 0:
            return None

        # Handle looping
        if channel.loop:
            elapsed = elapsed % total_duration
        elif elapsed >= total_duration:
            # Non-looping playlist has ended, return last item at end position
            last_item = playlist_items[-1]
            return (last_item.file_path, last_item.duration, last_item.title)

        # Find current item and seek position
        accumulated = 0
        for item in playlist_items:
            if accumulated + item.duration > elapsed:
                seek = elapsed - accumulated
                return (item.file_path, seek, item.title)
            accumulated += item.duration

        # Fallback (shouldn't reach here)
        return (playlist_items[0].file_path, 0, playlist_items[0].title)

    def get_upcoming_programs(self, channel: Channel, hours_ahead: int = 6) -> list:
        """
        Get upcoming programs for EPG generation.

        Returns:
            List of tuples: (start_time, end_time, title, description)
        """
        # Resolve playlist items
        from app.services.playlist_manager import playlist_manager

        playlist_items = []
        if channel.playlist_id:
            playlist = playlist_manager.get_playlist(channel.playlist_id)
            if playlist:
                playlist_items = playlist.items
        elif channel.playlist:
            # Fallback to embedded playlist for backward compatibility
            playlist_items = channel.playlist

        if not playlist_items:
            return []

        programs = []
        now_utc = datetime.now(timezone.utc)

        # Calculate starting position
        if channel.start_time:
            start_ref = channel.start_time.replace(tzinfo=timezone.utc)
            elapsed = (now_utc - start_ref).total_seconds()
        else:
            start_ref = datetime.fromtimestamp(0, tz=timezone.utc)
            elapsed = now_utc.timestamp()

        total_duration = sum(item.duration for item in playlist_items)
        if total_duration == 0:
            return []

        # Handle looping to find current position
        if channel.loop and elapsed >= 0:
            elapsed = elapsed % total_duration

        # Generate programs
        current_time = now_utc
        end_time = now_utc.timestamp() + (hours_ahead * 3600)

        playlist_index = 0
        position_in_playlist = 0

        # Find current position in playlist
        if elapsed >= 0:
            for i, item in enumerate(playlist_items):
                if position_in_playlist + item.duration > elapsed:
                    playlist_index = i
                    # Start from current position in current item
                    current_time = now_utc
                    break
                position_in_playlist += item.duration

        # Generate upcoming programs
        iterations = 0
        max_iterations = 1000  # Prevent infinite loops

        while current_time.timestamp() < end_time and iterations < max_iterations:
            iterations += 1
            item = playlist_items[playlist_index]

            program_start = current_time
            program_end = datetime.fromtimestamp(
                current_time.timestamp() + item.duration,
                tz=timezone.utc
            )

            programs.append((
                program_start,
                program_end,
                item.title,
                item.description or ""
            ))

            current_time = program_end
            playlist_index = (playlist_index + 1) % len(playlist_items)

            # If not looping and reached end, stop
            if not channel.loop and playlist_index == 0 and iterations > 0:
                break

        return programs


# Global instance
playlist_scheduler = PlaylistScheduler()
