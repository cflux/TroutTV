# Portainer Deployment - Summary

Your TroutTV project is now fully configured for Portainer stack deployment!

## Files Created for Portainer

### 1. `docker-compose.yml` (Updated)
- ✓ Uses pre-built image instead of building
- ✓ Named volumes for persistent data
- ✓ Comprehensive environment variables with comments
- ✓ Health check configuration
- ✓ Portainer-friendly labels
- ✓ Example configurations for common scenarios

### 2. `portainer-stack.yml` (New)
- ✓ Clean template ready to paste into Portainer
- ✓ Clear instructions in comments
- ✓ Highlights what needs to be customized
- ✓ Simplified for stack deployment

### 3. `PORTAINER_DEPLOY.md` (New)
Comprehensive deployment guide with:
- ✓ Step-by-step instructions
- ✓ Pre-deployment checklist
- ✓ Configuration examples (Windows/Linux)
- ✓ Troubleshooting section
- ✓ Backup/restore procedures
- ✓ Advanced configurations (Traefik, hardware acceleration)
- ✓ IPTV client setup guides

### 4. `PORTAINER_QUICKSTART.txt` (New)
- ✓ One-page quick reference
- ✓ Copy-paste commands
- ✓ Common issues and solutions
- ✓ Port configuration guide
- ✓ File path examples

### 5. `README.md` (Updated)
- ✓ Added Portainer section at top of Quick Start
- ✓ Links to Portainer guides
- ✓ Updated Docker Compose instructions

## Deployment Process (Quick Overview)

### Step 1: Build the Image
```bash
cd D:\claude\TroutTV
docker build -t trouttv:latest .
```

### Step 2: Prepare Configuration
- Get your server IP: `ipconfig` (Windows) or `ip addr` (Linux)
- Note your media directory path
- Example: `D:\Media` or `/mnt/media`

### Step 3: Deploy in Portainer
1. Open Portainer → Stacks → Add stack
2. Name: `trouttv`
3. Build method: Web editor
4. Copy content from `portainer-stack.yml`
5. Update these lines:
   ```yaml
   - D:/YOUR/MEDIA/PATH:/data/media      # Line ~31
   - BASE_URL=http://YOUR_IP:8000        # Line ~38
   ```
6. Deploy the stack

### Step 4: Verify
- Check container status (should be green/healthy)
- Access: http://YOUR_IP:8000
- Test health: http://YOUR_IP:8000/health

## Key Configuration Points

### Critical Settings to Update

1. **BASE_URL** (Most Important!)
   ```yaml
   - BASE_URL=http://192.168.1.100:8000
   ```
   This MUST match your server's IP address. This is what clients will use to access streams.

2. **Media Volume**
   ```yaml
   # Windows:
   - D:/Media:/data/media

   # Linux:
   - /mnt/media:/data/media
   ```
   Point to where your video files are stored.

3. **Port Mapping** (if 8000 is in use)
   ```yaml
   - "8080:8000"  # Host:Container
   ```
   And update BASE_URL to match!

### Optional Settings

- `STREAM_TIMEOUT`: 60 (seconds before stopping idle streams)
- `CLEANUP_INTERVAL`: 30 (seconds between cleanup checks)
- `EPG_DAYS_AHEAD`: 2 (days of EPG data)

## Volume Strategy

### Named Volumes (Docker Managed)
- `trouttv_channels` → Channel configurations (persistent)
- `trouttv_streams` → HLS segments (temporary, can be cleared)

**Backup**: Use Portainer's volume browser or:
```bash
docker run --rm -v trouttv_channels:/data -v $(pwd):/backup alpine tar czf /backup/channels-backup.tar.gz /data
```

### Bind Mount (Your Media)
- Maps directly to your host directory
- Read-only access for the container
- No Docker volume management needed

## File Paths in Channels

When creating channels in the web UI:

**Your actual path:** `D:\Media\Movies\Inception.mp4`
**In channel config:** `/data/media/Movies/Inception.mp4`

The `/data/media` part is the container mount point. Everything after that matches your folder structure.

## Testing Your Deployment

### 1. Check Container Health
```bash
curl http://YOUR_IP:8000/health
```
Expected: `{"status":"healthy","active_streams":0}`

### 2. Access Web UI
Open browser: `http://YOUR_IP:8000`

### 3. Create Test Channel
- Name: Test
- Number: 1
- Add item with path: `/data/media/test.mp4`

### 4. Download M3U
Click "Download M3U" or visit:
`http://YOUR_IP:8000/playlist.m3u`

### 5. Test in VLC
```
VLC → Media → Open Network Stream
URL: http://YOUR_IP:8000/playlist.m3u
```

## Common Scenarios

### Scenario 1: Basic Home Server
```yaml
ports:
  - "8000:8000"
volumes:
  - /home/user/Videos:/data/media
environment:
  - BASE_URL=http://192.168.1.50:8000
```

### Scenario 2: Custom Port (8000 in use)
```yaml
ports:
  - "8080:8000"
environment:
  - BASE_URL=http://192.168.1.50:8080
```

### Scenario 3: Windows Media Server
```yaml
volumes:
  - D:/Media:/data/media
  - E:/Movies:/data/movies  # Additional mount
environment:
  - BASE_URL=http://192.168.1.100:8000
```

### Scenario 4: External Access (with domain)
```yaml
environment:
  - BASE_URL=https://tv.yourdomain.com
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.trouttv.rule=Host(`tv.yourdomain.com`)"
```

## Troubleshooting Quick Reference

| Issue | Check | Solution |
|-------|-------|----------|
| Container won't start | Portainer logs | Image built? `docker images \| grep trouttv` |
| Can't access web UI | Firewall | Allow port in firewall settings |
| Streams won't play | File paths | Use `/data/media/...` not `D:\...` |
| Health check fails | Wait time | Allow 40s for startup |
| Wrong stream URLs | BASE_URL | Must match your server IP |

## Next Steps

1. **Deploy the stack** following the guides
2. **Add your media files** to the configured directory
3. **Create channels** via web UI
4. **Test streaming** with VLC
5. **Configure IPTV clients** (Jellyfin, Plex, etc.)

## Support Resources

- **Full deployment guide**: PORTAINER_DEPLOY.md
- **Quick reference**: PORTAINER_QUICKSTART.txt
- **General documentation**: README.md
- **Quick start**: QUICKSTART.md
- **Project status**: PROJECT_STATUS.md

## Quick Links (After Deployment)

Replace `YOUR_IP` with your server's IP address:

- Web UI: http://YOUR_IP:8000
- M3U Playlist: http://YOUR_IP:8000/playlist.m3u
- XMLTV EPG: http://YOUR_IP:8000/xmltv.xml
- API Docs: http://YOUR_IP:8000/docs
- Health Check: http://YOUR_IP:8000/health
- Stream (direct): http://YOUR_IP:8000/stream/CHANNEL_ID/master.m3u8

---

**You're all set! Your TroutTV deployment is Portainer-ready.**

Just build the image, paste the stack configuration, update your settings, and deploy!
