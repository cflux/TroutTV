# TroutTV Streaming Troubleshooting Guide

## Common Issues with VLC/Media Players

### Issue: VLC won't open M3U or stream URLs

This is usually caused by one of these problems:

## 1. **CRITICAL: Fix BASE_URL Configuration**

The most common issue is using `localhost` in the BASE_URL.

### Find Your IP Address:
1. Open Command Prompt
2. Run: `ipconfig`
3. Look for "IPv4 Address" under your active network adapter (usually Ethernet or Wi-Fi)
4. It will look like: `192.168.1.XXX` or `10.0.0.XXX`

### Update .env File:
1. Open `.env` in a text editor
2. Change this line:
   ```
   BASE_URL=http://localhost:8000
   ```
   To your actual IP (example):
   ```
   BASE_URL=http://192.168.1.100:8000
   ```
3. **IMPORTANT:** Use your actual IP address, not localhost!

## 2. **Restart the Server**

After changing `.env`, you MUST restart:
```bash
# Stop the server (Ctrl+C)
# Then start again:
python run.py
```

## 3. **Run Diagnostic Tests**

Test your setup:
```bash
python test_stream.py
```

This will check:
- ✓ Server is running
- ✓ Channels are configured
- ✓ M3U playlist is accessible
- ✓ FFmpeg is working
- ✓ Streams can start

## 4. **Test in VLC**

### Method 1: Open Network Stream
1. Open VLC
2. Media → Open Network Stream
3. Enter: `http://YOUR_IP:8000/playlist.m3u`
4. Click Play

### Method 2: Open Playlist URL Directly
1. Get the playlist URL: `http://YOUR_IP:8000/playlist.m3u`
2. Download it as a file
3. Open the file in VLC

### Method 3: Open Individual Channel
1. Get channel master URL: `http://YOUR_IP:8000/stream/CHANNEL_ID/master.m3u8`
2. Open in VLC as network stream

## 5. **Check Firewall**

Windows Firewall might block connections:

1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Make sure Python is allowed on Private networks
4. Or temporarily disable firewall to test

## 6. **Verify Channels Have Media**

1. Open web UI: `http://localhost:8000`
2. Check channels have:
   - ✓ At least one playlist item
   - ✓ Valid media file paths
   - ✓ Channel is enabled (green)

## 7. **Check FFmpeg**

FFmpeg must be installed and in PATH:

```bash
ffmpeg -version
```

If this fails:
- Download FFmpeg from https://ffmpeg.org/download.html
- Add to Windows PATH
- Restart terminal/server

## 8. **Check Server Logs**

When you try to play a stream, watch the server console for errors:
- File not found errors
- FFmpeg errors
- Permission errors

## Common Error Messages

### "Stream playlist not found"
- Stream hasn't started yet (wait 2-3 seconds)
- FFmpeg failed to start
- Check server logs for FFmpeg errors

### "Channel not found"
- Channel ID is wrong
- Channel is disabled
- Check web UI for correct channel ID

### "No media to play"
- Playlist is empty
- Media file paths are wrong
- Media files don't exist

## Still Not Working?

1. Run the diagnostic: `python test_stream.py`
2. Check server console for errors
3. Verify your IP address is correct in `.env`
4. Try accessing from the same computer first
5. Make sure port 8000 isn't blocked by firewall

## Testing Checklist

- [ ] `.env` file exists with correct IP address (not localhost)
- [ ] Server restarted after changing `.env`
- [ ] FFmpeg installed and working
- [ ] At least one enabled channel with media files
- [ ] Media files actually exist at the specified paths
- [ ] Firewall allows Python/port 8000
- [ ] Tested with diagnostic script
- [ ] Can access web UI at `http://YOUR_IP:8000`
