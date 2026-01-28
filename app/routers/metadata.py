from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response
from app.services.channel_manager import channel_manager
from app.services.m3u_generator import m3u_generator
from app.services.xmltv_generator import xmltv_generator
from app.config import settings

router = APIRouter(tags=["metadata"])


@router.get("/playlist.m3u")
async def get_m3u_playlist():
    """Generate M3U playlist for IPTV clients."""
    channels = channel_manager.list_channels()
    m3u_content = m3u_generator.generate_m3u(channels, settings.base_url)

    return PlainTextResponse(
        content=m3u_content,
        media_type="audio/x-mpegurl"
    )


@router.get("/xmltv.xml")
async def get_xmltv_epg():
    """Generate XMLTV EPG data."""
    channels = channel_manager.list_channels()
    xmltv_content = xmltv_generator.generate_xmltv(channels)

    return Response(
        content=xmltv_content,
        media_type="application/xml"
    )
