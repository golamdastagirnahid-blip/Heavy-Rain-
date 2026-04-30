"""
Video Processor
720p output - Fast processing
High quality audio
No thumbnail embedding
"""

import os
import json
import math
import subprocess


OUTPUT_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "output"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_PART_SECONDS = 4 * 60 * 60


class VideoProcessor:

    def get_duration(self, file_path):
        """Get duration in seconds"""
        try:
            cmd = [
                "ffprobe",
                "-v",            "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            result = subprocess.run(
                cmd,
                capture_output = True,
                text           = True,
                timeout        = 30
            )
            if result.returncode != 0:
                return 0
            data = json.loads(result.stdout)
            return float(
                data["format"]["duration"]
            )
        except Exception as e:
            print(f"   ⚠️ Duration error: {e}")
            return 0

    def calculate_parts(self, audio_duration):
        """Calculate number of 4-hour parts"""
        return max(
            1,
            math.ceil(
                audio_duration / MAX_PART_SECONDS
            )
        )

    def format_duration(self, seconds):
        hours   = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

    def create_video(
        self,
        audio_path,
        footage_path,
        output_id,
        start_sec,
        end_sec,
        thumbnail_path = None
    ):
        """
        Create 720p video
        Loop footage over audio segment
        High quality audio
        Fast processing
        """
        output_path = os.path.join(
            OUTPUT_DIR,
            f"{output_id}.mp4"
        )

        duration = end_sec - start_sec

        print(
            f"   🎥 Creating: "
            f"{self.format_duration(duration)}"
        )
        print(f"   📐 Quality  : 720p HD")
        print(f"   🎵 Audio    : 192k HQ")
        print(f"   ⚡ Speed    : ultrafast")

        try:
            cmd = [
                "ffmpeg",
                "-y",

                # ── Loop footage ──
                "-stream_loop", "-1",
                "-i", footage_path,

                # ── Audio segment ──
                "-ss", str(int(start_sec)),
                "-t",  str(int(duration)),
                "-i",  audio_path,

                # ── Map streams ──
                "-map", "0:v:0",
                "-map", "1:a:0",

                # ── Video 720p fast ──
                "-c:v",       "libx264",
                "-preset",    "ultrafast",
                "-tune",      "fastdecode",
                "-crf",       "28",
                "-vf", (
                    "scale=1280:720:"
                    "force_original_aspect_ratio"
                    "=increase,"
                    "crop=1280:720,"
                    "fps=24"
                ),
                "-profile:v", "baseline",
                "-level",     "3.1",
                "-pix_fmt",   "yuv420p",

                # ── High quality audio ──
                "-c:a",  "aac",
                "-b:a",  "192k",
                "-ar",   "48000",
                "-ac",   "2",
                "-profile:a", "aac_low",

                # ── Duration ──
                "-t",       str(int(duration)),
                "-shortest",

                # ── Clean output ──
                "-sn",
                "-map_metadata", "-1",
                "-threads",      "0",

                output_path
            ]

            print("   ⚙️ FFmpeg running...")

            result = subprocess.run(
                cmd,
                capture_output = True,
                text           = True,
                timeout        = 14400
            )

            if result.returncode == 0:
                if os.path.exists(output_path):
                    size = os.path.getsize(
                        output_path
                    )
                    print(
                        f"   ✅ Video ready: "
                        f"{size // 1024 // 1024} MB"
                    )
                    return output_path
                print("   ❌ Output missing")
                return None
            else:
                print(
                    f"   ❌ FFmpeg failed:\n"
                    f"{result.stderr[-200:]}"
                )
                return None

        except subprocess.TimeoutExpired:
            print("   ❌ FFmpeg timeout")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
