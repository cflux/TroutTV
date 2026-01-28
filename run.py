#!/usr/bin/env python3
"""
TroutTV IPTV Server - Startup Script
"""

if __name__ == "__main__":
    import uvicorn
    from app.config import settings

    print("=" * 60)
    print("TroutTV IPTV Server")
    print("=" * 60)
    print(f"Starting server on {settings.host}:{settings.port}")
    print(f"Access web UI at: {settings.base_url}")
    print(f"M3U Playlist: {settings.base_url}/playlist.m3u")
    print(f"XMLTV EPG: {settings.base_url}/xmltv.xml")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="info"
    )
