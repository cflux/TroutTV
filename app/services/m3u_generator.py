from typing import List
from app.models.channel import Channel


class M3UGenerator:
    def generate_m3u(self, channels: List[Channel], base_url: str) -> str:
        """
        Generate M3U playlist for IPTV clients.

        Format:
        #EXTM3U
        #EXTINF:-1 tvg-id="channel1" tvg-name="Channel 1" tvg-logo="http://..." group-title="Movies",Channel 1
        http://server:8000/stream/channel1/master.m3u8
        """
        lines = ["#EXTM3U"]

        for channel in channels:
            if not channel.enabled:
                continue

            # Build EXTINF line
            extinf_parts = ["#EXTINF:-1"]

            # Add tvg attributes
            extinf_parts.append(f'tvg-id="{channel.id}"')
            extinf_parts.append(f'tvg-name="{channel.name}"')
            extinf_parts.append(f'tvg-chno="{channel.number}"')

            if channel.logo_url:
                extinf_parts.append(f'tvg-logo="{channel.logo_url}"')

            extinf_parts.append(f'group-title="{channel.category}"')

            # Channel name at the end
            extinf_line = " ".join(extinf_parts) + f",{channel.name}"
            lines.append(extinf_line)

            # Stream URL
            stream_url = f"{base_url}/stream/{channel.id}/master.m3u8"
            lines.append(stream_url)

        return "\n".join(lines) + "\n"


# Global instance
m3u_generator = M3UGenerator()
