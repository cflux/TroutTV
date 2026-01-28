# TroutTV Portainer Deployment Guide

This guide will help you deploy TroutTV as a stack in Portainer.

## Prerequisites

- Portainer installed and running
- Docker installed on your host
- Access to your media files directory

## Deployment Steps

### Step 1: Build the Docker Image

Since Portainer stacks can't build images, you need to build the image first on your Docker host.

**Option A: Build Locally (Recommended)**

1. Open terminal/PowerShell on your Docker host
2. Navigate to the TroutTV directory:
   ```bash
   cd D:\claude\TroutTV
   ```

3. Build the Docker image:
   ```bash
   docker build -t trouttv:latest .
   ```

4. Verify the image was created:
   ```bash
   docker images | grep trouttv
   ```
   You should see: `trouttv    latest    [IMAGE_ID]    [DATE]    [SIZE]`

**Option B: Use Docker Registry (Advanced)**

If you want to deploy across multiple hosts:

1. Build the image:
   ```bash
   docker build -t yourusername/trouttv:latest .
   ```

2. Push to Docker Hub:
   ```bash
   docker login
   docker push yourusername/trouttv:latest
   ```

3. Update `docker-compose.yml` to use your registry image:
   ```yaml
   image: yourusername/trouttv:latest
   ```

---

### Step 2: Prepare Your Configuration

1. **Find your server's IP address:**
   - Windows: `ipconfig` (look for IPv4 Address)
   - Linux: `ip addr` or `hostname -I`

2. **Locate your media directory:**
   - Example: `D:/Media` (Windows)
   - Example: `/mnt/media` (Linux)

3. **Note the port you want to use:**
   - Default: 8000
   - Change if port is already in use

---

### Step 3: Deploy Stack in Portainer

1. **Login to Portainer**
   - Open Portainer in your browser (usually http://localhost:9000)

2. **Navigate to Stacks**
   - Click "Stacks" in the left menu
   - Click "+ Add stack"

3. **Configure Stack**
   - **Name:** `trouttv`
   - **Build method:** Select "Web editor"

4. **Copy the docker-compose.yml content**

   Copy the content from `docker-compose.yml` or use this template:

```yaml
version: '3.8'

services:
  trouttv:
    image: trouttv:latest
    container_name: trouttv
    hostname: trouttv

    ports:
      - "8000:8000"

    volumes:
      - trouttv_channels:/data/channels
      - trouttv_streams:/streams
      # CHANGE THIS to your media directory!
      - /path/to/your/media:/data/media

    environment:
      - HOST=0.0.0.0
      - PORT=8000
      # CHANGE THIS to your server's IP!
      - BASE_URL=http://192.168.1.100:8000
      - CHANNELS_DIR=/data/channels
      - MEDIA_DIR=/data/media
      - STREAMS_DIR=/streams
      - STREAM_TIMEOUT=60
      - CLEANUP_INTERVAL=30
      - EPG_DAYS_AHEAD=2
      - FFMPEG_PATH=ffmpeg
      - FFPROBE_PATH=ffprobe

    restart: unless-stopped

    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    labels:
      - "com.trouttv.description=IPTV Streaming Server"
      - "com.trouttv.version=1.0.0"

volumes:
  trouttv_channels:
    driver: local
  trouttv_streams:
    driver: local
```

5. **Customize the configuration:**

   **IMPORTANT: Update these values before deploying!**

   - **Media directory** (line ~18):
     ```yaml
     # Windows:
     - D:/Media:/data/media

     # Linux:
     - /mnt/media:/data/media
     ```

   - **BASE_URL** (line ~25):
     ```yaml
     # Use your server's IP address:
     - BASE_URL=http://192.168.1.100:8000

     # Or domain name:
     - BASE_URL=http://trouttv.example.com:8000
     ```

   - **Port** (if 8000 is in use, change the first number):
     ```yaml
     # Use port 8080 instead:
     - "8080:8000"

     # Don't forget to update BASE_URL too!
     - BASE_URL=http://192.168.1.100:8080
     ```

6. **Deploy the stack**
   - Click "Deploy the stack"
   - Wait for deployment to complete

---

### Step 4: Verify Deployment

1. **Check container status in Portainer:**
   - Go to "Containers" in left menu
   - Look for "trouttv" container
   - Status should be "running" with green dot
   - Health should show "healthy" after ~40 seconds

2. **Check logs:**
   - Click on the "trouttv" container
   - Click "Logs"
   - You should see:
     ```
     Starting TroutTV IPTV Server...
     FFmpeg found: ffmpeg
     Hardware acceleration: qsv (or software)
     Server ready at http://...
     ```

3. **Access the web UI:**
   - Open browser to: http://YOUR_SERVER_IP:8000
   - You should see the TroutTV interface

4. **Test health endpoint:**
   - Open: http://YOUR_SERVER_IP:8000/health
   - Should return: `{"status":"healthy","active_streams":0}`

---

### Step 5: Configure Channels

1. **Access web UI:**
   ```
   http://YOUR_SERVER_IP:8000
   ```

2. **Add your first channel:**
   - Click "Add Channel"
   - Fill in details:
     - Name: "Test Channel"
     - Number: 1
     - Category: "General"
   - Add playlist item:
     - File Path: `/data/media/yourfile.mp4` (path inside container)
     - Duration: Video length in seconds
     - Title: "Test Video"
   - Click "Save Channel"

3. **Download M3U playlist:**
   - Click "Download M3U" button
   - Or access directly: http://YOUR_SERVER_IP:8000/playlist.m3u

4. **Test in VLC:**
   - Open VLC
   - Media → Open Network Stream
   - URL: `http://YOUR_SERVER_IP:8000/playlist.m3u`
   - Click Play

---

## Configuration Guide

### Media File Paths

When creating channels, use paths relative to the container's `/data/media` directory:

**Your media location:** `D:\Media\Movies\movie.mp4`
**In container:** `/data/media/Movies/movie.mp4`

**Path in channel config:** `/data/media/Movies/movie.mp4`

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | http://localhost:8000 | Public URL for M3U/EPG links |
| `PORT` | 8000 | Internal container port |
| `STREAM_TIMEOUT` | 60 | Seconds before stopping idle streams |
| `CLEANUP_INTERVAL` | 30 | Seconds between cleanup checks |
| `EPG_DAYS_AHEAD` | 2 | Days of EPG data to generate |

### Volume Mapping

| Volume | Container Path | Purpose |
|--------|---------------|---------|
| `trouttv_channels` | `/data/channels` | Channel JSON configs (persistent) |
| `trouttv_streams` | `/streams` | HLS segments (temporary) |
| Your media dir | `/data/media` | Your video files (read-only) |

---

## Updating the Stack

To update configuration:

1. In Portainer, go to "Stacks"
2. Click on "trouttv" stack
3. Click "Editor"
4. Make your changes
5. Click "Update the stack"
6. Check "Re-pull image and redeploy" if you rebuilt the image
7. Click "Update"

---

## Backup and Restore

### Backup Channel Configurations

**Option 1: Using Portainer**
1. Go to "Volumes"
2. Click on "trouttv_channels"
3. Click "Browse"
4. Download all .json files

**Option 2: Using Docker**
```bash
# Copy from volume to host
docker run --rm -v trouttv_channels:/data -v $(pwd):/backup alpine tar czf /backup/channels-backup.tar.gz /data
```

### Restore Channel Configurations

```bash
# Extract backup to volume
docker run --rm -v trouttv_channels:/data -v $(pwd):/backup alpine tar xzf /backup/channels-backup.tar.gz -C /
```

---

## Troubleshooting

### Container won't start

1. **Check logs in Portainer:**
   - Containers → trouttv → Logs

2. **Common issues:**
   - Image not found: Build the image first (Step 1)
   - Port already in use: Change port mapping
   - Media directory not found: Check volume mapping

### Can't access web UI

1. **Check container is running:**
   - Portainer → Containers → trouttv should be green

2. **Check firewall:**
   - Windows: Allow port 8000 in Windows Firewall
   - Linux: `sudo ufw allow 8000`

3. **Verify port mapping:**
   - Portainer → Containers → trouttv → Port configuration

### Streams won't play

1. **Check media file paths:**
   - Paths should be `/data/media/...` (container path)
   - Verify files exist in mapped directory

2. **Check FFmpeg:**
   - Portainer → Containers → trouttv → Logs
   - Look for FFmpeg errors

3. **Check stream status:**
   - Open: http://YOUR_IP:8000/stream/CHANNEL_ID/status

### Healthcheck failing

1. **Wait 40 seconds** - Initial startup takes time

2. **Check port 8000 is accessible:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Check container logs** for startup errors

---

## Advanced Configuration

### Using with Traefik Reverse Proxy

If you use Traefik, update the labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.trouttv.rule=Host(`trouttv.yourdomain.com`)"
  - "traefik.http.routers.trouttv.entrypoints=websecure"
  - "traefik.http.routers.trouttv.tls.certresolver=letsencrypt"
  - "traefik.http.services.trouttv.loadbalancer.server.port=8000"
```

### Using Custom Network

Uncomment the network section in docker-compose.yml:

```yaml
services:
  trouttv:
    networks:
      - trouttv_network

networks:
  trouttv_network:
    driver: bridge
```

### Hardware Acceleration (Intel QSV)

Add device mapping for Intel GPU:

```yaml
devices:
  - /dev/dri:/dev/dri
```

Then in channel settings, select "Intel QSV" transcode preset.

---

## IPTV Client Configuration

### Jellyfin

1. Dashboard → Live TV → Tuner Devices → Add
2. Type: M3U Tuner
3. M3U URL: `http://YOUR_SERVER_IP:8000/playlist.m3u`
4. Save
5. Dashboard → Live TV → TV Guide Data Providers → Add
6. Type: XMLTV
7. File or URL: `http://YOUR_SERVER_IP:8000/xmltv.xml`
8. Save and refresh guide

### Plex

1. Settings → Live TV & DVR
2. Setup Plex DVR
3. Select tuner device type
4. Enter M3U URL: `http://YOUR_SERVER_IP:8000/playlist.m3u`
5. For EPG: Use third-party tool to import XMLTV

### TiviMate / Other IPTV Apps

1. Add Playlist
2. Playlist Type: M3U URL
3. URL: `http://YOUR_SERVER_IP:8000/playlist.m3u`
4. EPG URL: `http://YOUR_SERVER_IP:8000/xmltv.xml`

---

## Support

For issues specific to:
- **Portainer:** Check Portainer documentation
- **TroutTV:** Check README.md and project documentation
- **Docker:** Check Docker documentation

## Quick Reference URLs

Once deployed, these URLs are available:

- **Web UI:** http://YOUR_SERVER_IP:8000
- **M3U Playlist:** http://YOUR_SERVER_IP:8000/playlist.m3u
- **XMLTV EPG:** http://YOUR_SERVER_IP:8000/xmltv.xml
- **API Docs:** http://YOUR_SERVER_IP:8000/docs
- **Health Check:** http://YOUR_SERVER_IP:8000/health

Replace `YOUR_SERVER_IP` with your actual server IP address!
