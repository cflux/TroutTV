# TroutTV Quick Start Guide

Get your IPTV server running in 5 minutes!

## Prerequisites

1. **Python 3.10+** - [Download](https://www.python.org/downloads/)
2. **FFmpeg** - [Download](https://ffmpeg.org/download.html)
   - Windows: Download from https://www.gyan.dev/ffmpeg/builds/
   - Add FFmpeg to your system PATH

## Installation

### Step 1: Verify Setup

Run the setup script to verify your environment:

```bash
python setup.py
```

This will check:
- Python version
- FFmpeg installation
- Directory structure
- Dependencies

### Step 2: Install Dependencies

If prompted by setup.py, install dependencies:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
python -m pip install -r requirements.txt
```

### Step 3: Start the Server

```bash
python run.py
```

The server will start on `http://localhost:8000`

## First Channel Setup

### Option 1: Use the Web UI (Recommended)

1. Open http://localhost:8000 in your browser
2. Click "Add Channel"
3. Fill in the details:
   - **Name**: "My First Channel"
   - **Number**: 1
   - **Category**: "General"
4. Add a playlist item:
   - **File Path**: Full path to a video file (e.g., `D:/Videos/movie.mp4`)
   - **Duration**: Video length in seconds (e.g., 600 for 10 minutes)
   - **Title**: "My Video"
5. Click "Save Channel"

### Option 2: Edit JSON Directly

1. Navigate to `data/channels/`
2. Edit `sample_channel.json`
3. Update the `file_path` to point to your media files
4. Save the file

## Testing

### Test in VLC

1. Open VLC Media Player
2. Media → Open Network Stream
3. Enter: `http://localhost:8000/playlist.m3u`
4. Click Play
5. Your channels should appear!

### Test Stream Directly

Open this URL in VLC or a web browser with HLS support:
```
http://localhost:8000/stream/sample_channel/master.m3u8
```

## Getting Media Duration

If you don't know the duration of your media files, use FFprobe:

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "path/to/video.mp4"
```

Or let the server auto-detect it (feature to be implemented).

## Common Issues

### "FFmpeg not found"
- Ensure FFmpeg is installed and added to your system PATH
- Test with: `ffmpeg -version`

### "Module not found" errors
- Run: `pip install -r requirements.txt`

### Stream won't play
- Check that the file path in your channel JSON is correct
- Verify the file exists and is a valid video file
- Check server logs for errors

### Cannot access web UI
- Ensure the server is running (check terminal output)
- Try: http://127.0.0.1:8000 instead of localhost
- Check if port 8000 is already in use

## Next Steps

1. **Add more channels** - Use the web UI to create multiple channels
2. **Configure EPG** - The XMLTV EPG is generated automatically at `/xmltv.xml`
3. **Use with Jellyfin/Plex**:
   - M3U URL: `http://localhost:8000/playlist.m3u`
   - EPG URL: `http://localhost:8000/xmltv.xml`
4. **Optimize encoding** - Use hardware acceleration (QSV/NVENC) for better performance
5. **Docker deployment** - See README.md for Docker setup

## URLs Reference

- **Web UI**: http://localhost:8000
- **M3U Playlist**: http://localhost:8000/playlist.m3u
- **XMLTV EPG**: http://localhost:8000/xmltv.xml
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Configuration

Edit `.env` file (create from `.env.example`) to customize:

```env
HOST=0.0.0.0
PORT=8000
BASE_URL=http://192.168.1.100:8000  # Change to your server IP
STREAM_TIMEOUT=60
```

## Support

For issues and questions, check:
- README.md for detailed documentation
- Server logs in the terminal
- FFmpeg logs in case of encoding issues

Enjoy your personal IPTV server!
