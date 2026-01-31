import json
import uuid
from pathlib import Path
from typing import List, Optional
from app.models.channel import Channel
from app.config import settings


class ChannelManager:
    def __init__(self):
        self.channels_dir = settings.channels_dir

    def list_channels(self) -> List[Channel]:
        """List all channels from JSON files."""
        channels = []
        for json_file in self.channels_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    channel = Channel(**data)
                    channels.append(channel)
            except Exception as e:
                print(f"Error loading channel {json_file}: {e}")

        # Sort by channel number
        channels.sort(key=lambda x: x.number)
        return channels

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a specific channel by ID."""
        json_file = self.channels_dir / f"{channel_id}.json"
        if not json_file.exists():
            return None

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Channel(**data)
        except Exception as e:
            print(f"Error loading channel {channel_id}: {e}")
            return None

    def create_channel(self, channel: Channel) -> Channel:
        """Create a new channel."""
        # Generate ID if not provided
        if not channel.id:
            channel.id = str(uuid.uuid4())

        # Ensure unique channel number
        existing_channels = self.list_channels()
        used_numbers = {ch.number for ch in existing_channels}
        if channel.number in used_numbers:
            # Find next available number
            channel.number = max(used_numbers) + 1 if used_numbers else 1

        # Save to file
        json_file = self.channels_dir / f"{channel.id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(channel.model_dump(mode='json'), f, indent=2, default=str)

        return channel

    def update_channel(self, channel_id: str, channel: Channel) -> Optional[Channel]:
        """Update an existing channel."""
        json_file = self.channels_dir / f"{channel_id}.json"
        if not json_file.exists():
            return None

        # Ensure ID matches
        channel.id = channel_id

        # Save to file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(channel.model_dump(mode='json'), f, indent=2, default=str)

        return channel

    def delete_channel(self, channel_id: str) -> bool:
        """Delete a channel and its associated logo file."""
        json_file = self.channels_dir / f"{channel_id}.json"
        if not json_file.exists():
            return False

        # Check if channel has a logo file to delete
        try:
            channel = self.get_channel(channel_id)
            if channel and channel.logo_url and channel.logo_url.startswith('/logos/'):
                # Extract filename from URL
                logo_filename = channel.logo_url.replace('/logos/', '')
                logo_file = settings.logos_dir / logo_filename
                if logo_file.exists():
                    logo_file.unlink()
        except Exception as e:
            print(f"Error deleting logo for channel {channel_id}: {e}")
            # Continue with channel deletion even if logo deletion fails

        json_file.unlink()
        return True


# Global instance
channel_manager = ChannelManager()
