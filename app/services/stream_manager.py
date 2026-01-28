import asyncio
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional
from app.models.stream import StreamStatus
from app.services.channel_manager import channel_manager
from app.services.playlist_scheduler import playlist_scheduler
from app.utils.ffmpeg import ffmpeg_builder
from app.config import settings


class StreamManager:
    def __init__(self):
        self.streams_dir = settings.streams_dir
        self.active_streams: Dict[str, subprocess.Popen] = {}
        self.stream_metadata: Dict[str, dict] = {}
        self.last_request_time: Dict[str, datetime] = {}

    async def start_stream(self, channel_id: str) -> bool:
        """
        Start FFmpeg stream for a channel.

        Returns:
            True if stream started successfully, False otherwise
        """
        # Check if stream is already active
        if channel_id in self.active_streams:
            process = self.active_streams[channel_id]
            if process.poll() is None:
                # Stream is still running
                self.track_request(channel_id)
                return True
            else:
                # Process died, clean up
                await self.stop_stream(channel_id)

        # Get channel configuration
        channel = channel_manager.get_channel(channel_id)
        if not channel or not channel.enabled:
            print(f"Channel {channel_id} not found or disabled")
            return False

        if not channel.playlist:
            print(f"Channel {channel_id} has empty playlist")
            return False

        # Get current media file and seek position
        media_info = playlist_scheduler.get_current_media(channel)
        if not media_info:
            print(f"No media to play for channel {channel_id}")
            return False

        file_path, seek, title = media_info

        # Verify file exists
        if not Path(file_path).exists():
            print(f"Media file not found: {file_path}")
            return False

        # Build FFmpeg command
        output_dir = self.streams_dir / channel_id
        cmd = ffmpeg_builder.build_hls_command(
            file_path,
            output_dir,
            seek,
            channel.stream_settings
        )

        # Start FFmpeg process
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL
            )

            self.active_streams[channel_id] = process
            self.stream_metadata[channel_id] = {
                'file_path': file_path,
                'title': title,
                'seek': seek,
                'start_time': datetime.now(timezone.utc)
            }
            self.track_request(channel_id)

            print(f"Started stream for channel {channel_id}: {title} (seek: {seek:.1f}s)")

            # Wait a bit for FFmpeg to generate initial segments
            await asyncio.sleep(2)

            return True

        except Exception as e:
            print(f"Error starting stream for channel {channel_id}: {e}")
            return False

    async def stop_stream(self, channel_id: str) -> bool:
        """
        Stop FFmpeg stream for a channel.

        Returns:
            True if stream was stopped, False if not running
        """
        if channel_id not in self.active_streams:
            return False

        process = self.active_streams[channel_id]

        # Terminate process
        try:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        except Exception as e:
            print(f"Error stopping stream {channel_id}: {e}")

        # Cleanup
        del self.active_streams[channel_id]
        if channel_id in self.stream_metadata:
            del self.stream_metadata[channel_id]
        if channel_id in self.last_request_time:
            del self.last_request_time[channel_id]

        # Delete stream directory
        output_dir = self.streams_dir / channel_id
        if output_dir.exists():
            try:
                shutil.rmtree(output_dir)
            except Exception as e:
                print(f"Error deleting stream directory {channel_id}: {e}")

        print(f"Stopped stream for channel {channel_id}")
        return True

    def track_request(self, channel_id: str):
        """Track that a request was made for this channel."""
        self.last_request_time[channel_id] = datetime.now(timezone.utc)

    def get_stream_status(self, channel_id: str) -> StreamStatus:
        """Get status of a stream."""
        is_active = channel_id in self.active_streams

        if is_active:
            metadata = self.stream_metadata.get(channel_id, {})
            return StreamStatus(
                channel_id=channel_id,
                is_active=True,
                current_file=metadata.get('file_path'),
                current_title=metadata.get('title'),
                seek_position=metadata.get('seek'),
                last_request=self.last_request_time.get(channel_id)
            )
        else:
            return StreamStatus(
                channel_id=channel_id,
                is_active=False
            )

    async def cleanup_idle_streams(self):
        """Stop streams that have been idle for too long."""
        now = datetime.now(timezone.utc)
        timeout = settings.stream_timeout

        channels_to_stop = []

        for channel_id, last_request in self.last_request_time.items():
            idle_time = (now - last_request).total_seconds()
            if idle_time > timeout:
                channels_to_stop.append(channel_id)

        for channel_id in channels_to_stop:
            print(f"Stopping idle stream: {channel_id}")
            await self.stop_stream(channel_id)

    async def stop_all_streams(self):
        """Stop all active streams."""
        channel_ids = list(self.active_streams.keys())
        for channel_id in channel_ids:
            await self.stop_stream(channel_id)


# Global instance
stream_manager = StreamManager()
