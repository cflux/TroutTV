import subprocess
from pathlib import Path
from typing import List, Optional
from app.models.channel import StreamSettings
from app.config import settings


class FFmpegBuilder:
    def __init__(self):
        self.ffmpeg_path = settings.ffmpeg_path

    def detect_hw_accel(self) -> str:
        """
        Detect available hardware acceleration.

        Returns:
            'qsv', 'nvenc', or 'software'
        """
        # Test for Intel QSV
        try:
            cmd = [self.ffmpeg_path, '-hide_banner', '-encoders']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            output = result.stdout + result.stderr

            # Check for QSV (Intel Quick Sync)
            if 'h264_qsv' in output:
                return 'qsv'

            # Check for NVENC (NVIDIA)
            if 'h264_nvenc' in output:
                return 'nvenc'

        except Exception as e:
            print(f"Error detecting hardware acceleration: {e}")

        return 'software'

    def build_hls_command(
        self,
        input_file: str,
        output_dir: Path,
        seek: float,
        stream_settings: StreamSettings
    ) -> List[str]:
        """
        Build FFmpeg command for HLS streaming.

        Args:
            input_file: Path to input media file
            output_dir: Directory for HLS output files
            seek: Seek position in seconds
            stream_settings: Stream configuration

        Returns:
            List of command arguments
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [self.ffmpeg_path]

        # Input options
        cmd.extend(['-hide_banner', '-loglevel', 'warning'])
        cmd.extend(['-re'])  # Real-time streaming

        # Seek to position
        if seek > 0:
            cmd.extend(['-ss', str(seek)])

        cmd.extend(['-i', input_file])

        # Video encoding based on preset
        preset = stream_settings.transcode_preset.lower()

        if preset == 'qsv':
            # Intel Quick Sync
            cmd.extend(['-c:v', 'h264_qsv'])
            cmd.extend(['-preset', 'veryfast'])
            cmd.extend(['-global_quality', '23'])
        elif preset == 'nvenc':
            # NVIDIA NVENC
            cmd.extend(['-c:v', 'h264_nvenc'])
            cmd.extend(['-preset', 'fast'])
            cmd.extend(['-cq', '23'])
        elif preset == 'software_medium':
            # Software encoding - medium preset
            cmd.extend(['-c:v', 'libx264'])
            cmd.extend(['-preset', 'medium'])
            cmd.extend(['-crf', '23'])
        else:
            # Software encoding - fast preset (default)
            cmd.extend(['-c:v', 'libx264'])
            cmd.extend(['-preset', 'veryfast'])
            cmd.extend(['-crf', '23'])

        # Video bitrate and buffer
        cmd.extend(['-maxrate', f'{stream_settings.video_bitrate}k'])
        cmd.extend(['-bufsize', f'{stream_settings.video_bitrate * 2}k'])

        # Resolution
        if stream_settings.resolution and stream_settings.resolution != 'original':
            cmd.extend(['-s', stream_settings.resolution])

        # Audio encoding
        cmd.extend(['-c:a', 'aac'])
        cmd.extend(['-b:a', f'{stream_settings.audio_bitrate}k'])
        cmd.extend(['-ar', '48000'])

        # HLS output options
        cmd.extend(['-f', 'hls'])
        cmd.extend(['-hls_time', str(stream_settings.segment_duration)])
        cmd.extend(['-hls_list_size', str(stream_settings.playlist_size)])
        cmd.extend(['-hls_flags', 'delete_segments+omit_endlist'])
        cmd.extend(['-hls_segment_type', 'mpegts'])

        # Output paths
        segment_pattern = str(output_dir / 'segment_%03d.ts')
        playlist_path = str(output_dir / 'stream.m3u8')

        cmd.extend(['-hls_segment_filename', segment_pattern])
        cmd.append(playlist_path)

        return cmd

    def test_ffmpeg(self) -> bool:
        """Test if FFmpeg is available."""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False


# Global instance
ffmpeg_builder = FFmpegBuilder()
