import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

from app.config import settings
from app.routers import channels, streaming, metadata, uploads
from app.services.stream_manager import stream_manager
from app.utils.ffmpeg import ffmpeg_builder


# Background task for cleanup
cleanup_task = None


async def cleanup_loop():
    """Background task to cleanup idle streams."""
    while True:
        try:
            await asyncio.sleep(settings.cleanup_interval)
            await stream_manager.cleanup_idle_streams()
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in cleanup loop: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("Starting TroutTV IPTV Server...")

    # Test FFmpeg
    if ffmpeg_builder.test_ffmpeg():
        print(f"FFmpeg found: {settings.ffmpeg_path}")
        hw_accel = ffmpeg_builder.detect_hw_accel()
        print(f"Hardware acceleration: {hw_accel}")
    else:
        print(f"WARNING: FFmpeg not found at {settings.ffmpeg_path}")

    # Start cleanup task
    global cleanup_task
    cleanup_task = asyncio.create_task(cleanup_loop())
    print(f"Cleanup task started (interval: {settings.cleanup_interval}s)")

    print(f"Server ready at {settings.base_url}")

    yield

    # Shutdown
    print("Shutting down TroutTV IPTV Server...")

    # Cancel cleanup task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass

    # Stop all streams
    await stream_manager.stop_all_streams()

    print("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="TroutTV IPTV Server",
    description="Transform media files into live TV channels with HLS streaming",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(channels.router)
app.include_router(streaming.router)
app.include_router(metadata.router)
app.include_router(uploads.router)

# Mount static files for web UI
web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    app.mount("/web", StaticFiles(directory=str(web_dir)), name="web")

# Mount static files for logos
if settings.logos_dir.exists():
    app.mount("/logos", StaticFiles(directory=str(settings.logos_dir)), name="logos")


@app.get("/")
async def root():
    """Redirect to web UI."""
    return RedirectResponse(url="/web/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_streams": len(stream_manager.active_streams)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
