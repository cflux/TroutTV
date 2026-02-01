"""
Migration script: Extract embedded playlists from channels.

Reads all channel JSON files, extracts their playlists, creates
separate playlist files, and updates channels to reference them.
"""

import json
import uuid
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def migrate_playlists():
    """Extract embedded playlists from channels and create separate playlist files."""
    channels_dir = Path("D:/claude/TroutTV/data/channels")
    playlists_dir = Path("D:/claude/TroutTV/data/playlists")

    # Ensure directories exist
    if not channels_dir.exists():
        print(f"Error: Channels directory not found: {channels_dir}")
        return False

    playlists_dir.mkdir(parents=True, exist_ok=True)

    playlist_map = {}  # channel_id -> playlist_id
    channels_processed = 0
    playlists_created = 0

    print("=" * 60)
    print("TroutTV Playlist Migration")
    print("=" * 60)
    print(f"Channels directory: {channels_dir}")
    print(f"Playlists directory: {playlists_dir}")
    print()

    # Process each channel
    channel_files = list(channels_dir.glob("*.json"))
    if not channel_files:
        print("No channel files found.")
        return True

    print(f"Found {len(channel_files)} channel file(s)\n")

    for channel_file in channel_files:
        try:
            with open(channel_file, 'r', encoding='utf-8') as f:
                channel_data = json.load(f)

            channel_id = channel_data.get('id', channel_file.stem)
            channel_name = channel_data.get('name', 'Unnamed Channel')
            embedded_playlist = channel_data.get('playlist', [])

            print(f"Processing: {channel_name} ({channel_id})")

            # Check if already migrated
            if channel_data.get('playlist_id'):
                print(f"  [SKIP] Already has playlist_id: {channel_data['playlist_id']}")
                channels_processed += 1
                continue

            if not embedded_playlist:
                print(f"  [SKIP] No playlist items, skipping")
                channels_processed += 1
                continue

            # Create playlist from embedded items
            playlist_id = str(uuid.uuid4())
            playlist_data = {
                "id": playlist_id,
                "name": f"{channel_name} Playlist",
                "description": f"Migrated from channel {channel_name}",
                "items": embedded_playlist,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "tags": ["migrated", channel_data.get('category', 'General').lower()]
            }

            # Save playlist
            playlist_file = playlists_dir / f"{playlist_id}.json"
            with open(playlist_file, 'w', encoding='utf-8') as f:
                json.dump(playlist_data, f, indent=2)

            print(f"  [OK] Created playlist: {playlist_id}")
            print(f"       Items: {len(embedded_playlist)}")
            playlists_created += 1

            # Update channel to reference playlist
            channel_data['playlist_id'] = playlist_id
            if 'scheduled_playlists' not in channel_data:
                channel_data['scheduled_playlists'] = []
            # Keep old 'playlist' field for rollback capability

            # Save updated channel
            with open(channel_file, 'w', encoding='utf-8') as f:
                json.dump(channel_data, f, indent=2)

            print(f"  [OK] Updated channel to reference playlist")

            playlist_map[channel_id] = playlist_id
            channels_processed += 1

        except Exception as e:
            print(f"  [ERROR] Error processing {channel_file}: {e}")
            continue

        print()

    # Save migration log
    log_file = playlists_dir / "_migration_log.json"
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({
                "migration_date": datetime.utcnow().isoformat() + "Z",
                "channels_processed": channels_processed,
                "playlists_created": playlists_created,
                "mapping": playlist_map
            }, f, indent=2)
        print(f"Migration log saved: {log_file}")
    except Exception as e:
        print(f"Warning: Could not save migration log: {e}")

    print()
    print("=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"Channels processed: {channels_processed}")
    print(f"Playlists created: {playlists_created}")
    print()

    if playlists_created > 0:
        print("[SUCCESS] Migration completed successfully!")
        print()
        print("Next steps:")
        print("1. Verify playlist files were created in data/playlists/")
        print("2. Test streaming a channel to ensure it still works")
        print("3. Deploy the updated TroutTV code")
    else:
        print("[INFO] No playlists were migrated (all channels already migrated or have no playlists)")

    return True


if __name__ == "__main__":
    print("\nWARNING: This script will modify your channel files.")
    print("Make sure you have backed up your data/channels/ directory!")
    print()

    response = input("Continue with migration? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Migration cancelled.")
        sys.exit(0)

    print()
    success = migrate_playlists()
    sys.exit(0 if success else 1)
