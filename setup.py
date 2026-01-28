#!/usr/bin/env python3
"""
TroutTV Setup and Verification Script
Run this before starting the server for the first time.
"""

import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.10+"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"  [OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  [FAIL] Python {version.major}.{version.minor}.{version.micro} (need 3.10+)")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\nChecking FFmpeg...")
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.decode().split('\n')[0]
            print(f"  [OK] {version_line}")
            return True
    except Exception as e:
        print(f"  [FAIL] FFmpeg not found: {e}")
        print("    Install FFmpeg: https://ffmpeg.org/download.html")
        return False


def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    dirs = [
        "app",
        "web",
        "data/channels",
        "data/media",
        "streams"
    ]
    all_exist = True
    for d in dirs:
        path = Path(d)
        if path.exists():
            print(f"  [OK] {d}")
        else:
            print(f"  [FAIL] {d} (missing)")
            all_exist = False
    return all_exist


def check_requirements():
    """Check if requirements.txt exists and is valid"""
    print("\nChecking requirements.txt...")
    req_file = Path("requirements.txt")
    if req_file.exists():
        print("  [OK] requirements.txt exists")
        with open(req_file) as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"    Found {len(packages)} packages")
        return True
    else:
        print("  [FAIL] requirements.txt not found")
        return False


def install_requirements():
    """Install Python requirements"""
    print("\n" + "="*60)
    response = input("Install Python dependencies? (y/n): ")
    if response.lower() != 'y':
        print("Skipping installation")
        return False

    print("\nInstalling requirements...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            check=True
        )
        print("  [OK] Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [FAIL] Installation failed: {e}")
        return False


def create_env_file():
    """Create .env file from example if it doesn't exist"""
    print("\nChecking .env file...")
    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("  [OK] .env file exists")
        return True

    if not env_example.exists():
        print("  [WARN] .env.example not found, skipping")
        return True

    print("  [WARN] .env file not found")
    response = input("Create .env from .env.example? (y/n): ")
    if response.lower() == 'y':
        with open(env_example) as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("  [OK] .env file created")
        print("    Edit .env to customize settings")
        return True

    return False


def main():
    """Run all setup checks"""
    print("="*60)
    print("TroutTV IPTV Server - Setup Verification")
    print("="*60)

    checks = [
        check_python_version(),
        check_ffmpeg(),
        check_directories(),
        check_requirements()
    ]

    if not all(checks):
        print("\n" + "="*60)
        print("Some checks failed. Please fix the issues above.")
        print("="*60)
        return False

    create_env_file()

    # Ask to install requirements
    try:
        import fastapi
        print("\n[OK] FastAPI already installed")
        deps_installed = True
    except ImportError:
        deps_installed = install_requirements()

    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Place your media files in data/media/")
    print("2. Edit channels in data/channels/ or use the web UI")
    print("3. Start the server:")
    print("   python run.py")
    print("\n4. Access the web UI at: http://localhost:8000")
    print("="*60)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
