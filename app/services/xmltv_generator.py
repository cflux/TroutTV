from typing import List
from lxml import etree
from datetime import datetime
from app.models.channel import Channel
from app.services.playlist_scheduler import playlist_scheduler
from app.config import settings


class XMLTVGenerator:
    def generate_xmltv(self, channels: List[Channel]) -> str:
        """
        Generate XMLTV EPG data.

        Format:
        <?xml version="1.0" encoding="UTF-8"?>
        <tv>
          <channel id="channel1">
            <display-name>Channel 1</display-name>
          </channel>
          <programme start="20260126120000 +0000" stop="20260126130000 +0000" channel="channel1">
            <title>Program Title</title>
            <desc>Program description</desc>
          </programme>
        </tv>
        """
        # Create root element
        tv = etree.Element("tv")
        tv.set("generator-info-name", "TroutTV")
        tv.set("generator-info-url", "https://github.com/yourusername/trouttv")

        # Add channels
        for channel in channels:
            if not channel.enabled:
                continue

            # Channel element
            channel_elem = etree.SubElement(tv, "channel")
            channel_elem.set("id", channel.id)

            display_name = etree.SubElement(channel_elem, "display-name")
            display_name.text = channel.name

            if channel.logo_url:
                icon = etree.SubElement(channel_elem, "icon")
                icon.set("src", channel.logo_url)

        # Add programs
        hours_ahead = settings.epg_days_ahead * 24

        for channel in channels:
            if not channel.enabled:
                continue

            programs = playlist_scheduler.get_upcoming_programs(channel, hours_ahead)

            for start_time, end_time, title, description in programs:
                programme = etree.SubElement(tv, "programme")
                programme.set("start", self._format_xmltv_time(start_time))
                programme.set("stop", self._format_xmltv_time(end_time))
                programme.set("channel", channel.id)

                title_elem = etree.SubElement(programme, "title")
                title_elem.set("lang", "en")
                title_elem.text = title

                if description:
                    desc_elem = etree.SubElement(programme, "desc")
                    desc_elem.set("lang", "en")
                    desc_elem.text = description

        # Convert to string
        xml_string = etree.tostring(
            tv,
            encoding='UTF-8',
            xml_declaration=True,
            pretty_print=True
        )
        return xml_string.decode('utf-8')

    def _format_xmltv_time(self, dt: datetime) -> str:
        """Format datetime as XMLTV time: YYYYMMDDHHmmss +0000"""
        return dt.strftime("%Y%m%d%H%M%S +0000")


# Global instance
xmltv_generator = XMLTVGenerator()
