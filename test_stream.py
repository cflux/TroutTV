#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TroutTV Stream Diagnostic Tool
Helps identify issues with streaming setup
"""

import requests
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
BASE_URL = "http://localhost:8000"


def test_server():
    """Test if the server is running."""
    print("1. Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Server is running")
            print(f"   ✓ Active streams: {data.get('active_streams', 0)}")
            return True
        else:
            print(f"   ✗ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ✗ Cannot connect to {BASE_URL}")
        print(f"   → Make sure the server is running with: python run.py")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_channels():
    """Test if channels are configured."""
    print("\n2. Testing channel configuration...")
    try:
        response = requests.get(f"{BASE_URL}/api/channels", timeout=5)
        if response.status_code == 200:
            channels = response.json()
            if len(channels) == 0:
                print(f"   ✗ No channels configured")
                print(f"   → Add channels via web UI at {BASE_URL}")
                return False

            print(f"   ✓ Found {len(channels)} channel(s)")
            for channel in channels:
                status = "enabled" if channel.get('enabled') else "disabled"
                playlist_count = len(channel.get('playlist', []))
                print(f"   - {channel.get('name')} (#{channel.get('number')}) - {status} - {playlist_count} items")
            return True
        else:
            print(f"   ✗ Failed to get channels: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_m3u_playlist():
    """Test if M3U playlist is accessible."""
    print("\n3. Testing M3U playlist...")
    try:
        response = requests.get(f"{BASE_URL}/playlist.m3u", timeout=5)
        if response.status_code == 200:
            content = response.text
            lines = content.split('\n')

            if not content.startswith('#EXTM3U'):
                print(f"   ✗ Invalid M3U format")
                return False

            # Count stream URLs
            stream_urls = [line for line in lines if line.startswith('http')]
            print(f"   ✓ M3U playlist accessible")
            print(f"   ✓ Contains {len(stream_urls)} stream URL(s)")

            # Show first stream URL for testing
            if stream_urls:
                print(f"\n   Test this URL in VLC:")
                print(f"   {stream_urls[0]}")

            return True
        else:
            print(f"   ✗ Failed to get M3U: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_stream_start(channel_id=None):
    """Test if a stream can start."""
    print("\n4. Testing stream start...")

    # Get first channel if not specified
    if not channel_id:
        try:
            response = requests.get(f"{BASE_URL}/api/channels", timeout=5)
            channels = response.json()
            if not channels:
                print("   ✗ No channels to test")
                return False

            # Get first enabled channel
            enabled_channels = [c for c in channels if c.get('enabled')]
            if not enabled_channels:
                print("   ✗ No enabled channels found")
                return False

            channel_id = enabled_channels[0]['id']
            channel_name = enabled_channels[0]['name']
            print(f"   Testing channel: {channel_name}")
        except Exception as e:
            print(f"   ✗ Error getting channels: {e}")
            return False

    # Try to access the master playlist
    try:
        master_url = f"{BASE_URL}/stream/{channel_id}/master.m3u8"
        print(f"   Requesting: {master_url}")

        response = requests.get(master_url, timeout=10)
        if response.status_code == 200:
            print(f"   ✓ Master playlist accessible")

            # Check if stream.m3u8 exists after a moment
            import time
            time.sleep(3)

            stream_url = f"{BASE_URL}/stream/{channel_id}/stream.m3u8"
            response = requests.get(stream_url, timeout=5)
            if response.status_code == 200:
                print(f"   ✓ Stream playlist accessible")
                print(f"\n   ✓ Stream started successfully!")
                print(f"\n   Open this URL in VLC:")
                print(f"   {master_url}")
                return True
            else:
                print(f"   ✗ Stream playlist not found: {response.status_code}")
                print(f"   → Check FFmpeg is installed and working")
                return False
        else:
            print(f"   ✗ Master playlist failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def check_ffmpeg():
    """Check if FFmpeg is available."""
    print("\n5. Checking FFmpeg...")
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True,
                              timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.decode().split('\n')[0]
            print(f"   ✓ {version_line}")
            return True
        else:
            print(f"   ✗ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print(f"   ✗ FFmpeg not found in PATH")
        print(f"   → Install FFmpeg: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main():
    """Run all diagnostic tests."""
    print("="*60)
    print("TroutTV Stream Diagnostic Tool")
    print("="*60)

    # Allow custom base URL
    if len(sys.argv) > 1:
        global BASE_URL
        BASE_URL = sys.argv[1]
        print(f"Using custom URL: {BASE_URL}\n")

    results = []

    results.append(test_server())
    if not results[-1]:
        print("\n" + "="*60)
        print("Server is not running. Start it first with: python run.py")
        print("="*60)
        sys.exit(1)

    results.append(test_channels())
    results.append(test_m3u_playlist())
    results.append(check_ffmpeg())
    results.append(test_stream_start())

    print("\n" + "="*60)
    if all(results):
        print("✓ All tests passed!")
        print("="*60)
        print("\nTry opening the M3U playlist in VLC:")
        print(f"{BASE_URL}/playlist.m3u")
        print("\nOr open a specific channel master playlist.")
    else:
        print("✗ Some tests failed")
        print("="*60)
        print("\nPlease fix the issues above and try again.")
    print("="*60)


if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Error: 'requests' module not installed")
        print("Install it with: pip install requests")
        sys.exit(1)

    main()
