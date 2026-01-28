# TroutTV IPTV Server

Transform media files into live TV channels with HLS streaming, XMLTV EPG, and M3U playlists.

## Features

- Transform local media files into live TV channels
- HLS streaming with adaptive bitrate support
- XMLTV EPG (Electronic Program Guide) generation
- M3U playlist generation for IPTV clients
- Web UI for channel management
- Hardware acceleration support (Intel QSV, NVIDIA NVENC)
- Docker support for easy deployment
- Compatible with VLC, Jellyfin, Plex, and other IPTV clients

## Requirements

- Python 3.10+
- FFmpeg (with hardware acceleration support optional)
- 8th gen Intel CPU or equivalent (recommended for multiple streams)

## Quick Start

### Using Portainer (Easiest for Docker Users)

If you manage Docker with Portainer, see the dedicated guide:

**→ [Portainer Deployment Guide](PORTAINER_DEPLOY.md)**

**→ [Portainer Quick Start](PORTAINER_QUICKSTART.txt)**

Quick summary:
1. Build image: `docker build -t trouttv:latest .`
2. In Portainer: Stacks → Add stack
3. Copy content from `portainer-stack.yml`
4. Update BASE_URL and media path
5. Deploy!

### Using Docker Compose

1. Clone or download this repository
2. Place your media files in `data/media/`
3. Build and start:

```bash
docker build -t trouttv:latest .
docker-compose up -d
```

4. Access the web UI at `http://localhost:8000`

### Manual Installation

1. Install Python 3.10+ and FFmpeg

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file (optional):

```env
HOST=0.0.0.0
PORT=8000
BASE_URL=http://192.168.1.100:8000
```

4. Start the server:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. Access the web UI at `http://localhost:8000`

## Usage

### Creating Channels

1. Open the web UI at `http://localhost:8000`
2. Click "Add Channel"
3. Fill in channel details:
   - Name, number, category
   - Logo URL (optional)
   - Stream settings (bitrate, resolution, encoding preset)
4. Add playlist items:
   - File path to your media files
   - Duration in seconds
   - Title and description
5. Click "Save Channel"

### Using with IPTV Clients

#### VLC

1. Open VLC
2. Media → Open Network Stream
3. Enter: `http://localhost:8000/playlist.m3u`
4. Play

#### Jellyfin

1. Dashboard → Live TV → Tuner Devices → Add
2. Type: M3U Tuner
3. M3U URL: `http://localhost:8000/playlist.m3u`
4. EPG Source: `http://localhost:8000/xmltv.xml`
5. Save and scan channels

#### Plex

1. Settings → Live TV & DVR → Set Up Plex DVR
2. Select HDHomeRun device (or other compatible)
3. Use `http://localhost:8000/playlist.m3u` as the channel source
4. Use `http://localhost:8000/xmltv.xml` for EPG

## Configuration

### Environment Variables

- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `BASE_URL` - Base URL for stream links (default: http://localhost:8000)
- `CHANNELS_DIR` - Directory for channel JSON files
- `MEDIA_DIR` - Directory for media files
- `STREAMS_DIR` - Directory for HLS segments (temp files)
- `STREAM_TIMEOUT` - Seconds before stopping idle streams (default: 60)
- `CLEANUP_INTERVAL` - Seconds between cleanup tasks (default: 30)
- `EPG_DAYS_AHEAD` - Days of EPG to generate (default: 2)

### Stream Settings

- **Video Bitrate**: 500-10000 kbps (3000 recommended for 720p)
- **Audio Bitrate**: 64-256 kbps (128 recommended)
- **Resolution**: Original, 480p, 720p, 1080p
- **Transcode Preset**:
  - Software Fast: Best compatibility, higher CPU usage
  - Software Medium: Better quality, even higher CPU usage
  - Intel QSV: Hardware acceleration for Intel CPUs (8th gen+)
  - NVIDIA NVENC: Hardware acceleration for NVIDIA GPUs

### Hardware Acceleration

To use hardware acceleration:

1. Ensure your hardware supports it (Intel QSV 8th gen+, NVIDIA GPU with NVENC)
2. Install appropriate drivers
3. Select the corresponding preset in stream settings
4. The server will auto-detect available encoders on startup

## API Endpoints

### Metadata

- `GET /playlist.m3u` - M3U playlist
- `GET /xmltv.xml` - XMLTV EPG

### Streaming

- `GET /stream/{channel_id}/master.m3u8` - HLS master playlist
- `GET /stream/{channel_id}/stream.m3u8` - HLS media playlist
- `GET /stream/{channel_id}/segment_*.ts` - HLS segments
- `GET /stream/{channel_id}/status` - Stream status

### Channel Management

- `GET /api/channels` - List all channels
- `GET /api/channels/{id}` - Get channel
- `POST /api/channels` - Create channel
- `PUT /api/channels/{id}` - Update channel
- `DELETE /api/channels/{id}` - Delete channel
- `POST /api/channels/{id}/restart` - Restart stream

## Directory Structure

```
TroutTV/
├── app/                    # Application code
│   ├── models/            # Pydantic models
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── web/                   # Web UI
│   ├── css/
│   ├── js/
│   └── index.html
├── data/
│   ├── channels/          # Channel JSON files
│   └── media/             # Your media files
├── streams/               # HLS segments (temp)
└── requirements.txt
```

## Troubleshooting

### Streams won't start

- Check that FFmpeg is installed: `ffmpeg -version`
- Verify media file paths are correct
- Check file permissions
- Look at server logs for errors

### Buffering or stuttering

- Reduce video bitrate in stream settings
- Use hardware acceleration if available
- Check network bandwidth
- Reduce number of concurrent streams

### EPG not showing in client

- Wait a few minutes for client to download EPG
- Try refreshing EPG in client settings
- Check that channel IDs match between M3U and XMLTV
- Verify XMLTV URL is accessible

### High CPU usage

- Enable hardware acceleration (QSV or NVENC)
- Use "Software Fast" preset instead of "Medium"
- Reduce video bitrate
- Reduce number of concurrent streams

## Development

### Running in development mode

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running tests

```bash
pytest
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open an issue on GitHub.
