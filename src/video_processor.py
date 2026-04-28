"""
Video Processor
Takes 1 stock footage clip and loops it
Combines with audio segment
Creates final MP4 video
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

# Maximum 4 hours per part
MAX_PART_SECONDS = 4 * 60 * 60


class VideoProcessor:

    def get_duration(self, file_path):
        """
        Get duration of any media file in seconds
        Uses ffprobe
        """
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
                print(
                    f"   ⚠️ ffprobe error: "
                    f"{result.stderr[:100]}"
                )
                return 0

            data     = json.loads(result.stdout)
            duration = float(
                data["format"]["duration"]
            )
            return duration

        except Exception as e:
            print(f"   ⚠️ Duration error: {e}")
            return 0

    def calculate_parts(self, audio_duration):
        """
        Calculate how many 4-hour parts needed
        """
        num_parts = math.ceil(
            audio_duration / MAX_PART_SECONDS
        )
        return max(1, num_parts)

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
        thumbnail_path=None
    ):
        """
        Create video by looping footage over audio
        - Takes 1 stock clip
        - Loops it until audio ends
        - Scales to 1920x1080
        - Returns output file path
        """
        output_path = os.path.join(
            OUTPUT_DIR,
            f"{output_id}.mp4"
        )

        duration = end_sec - start_sec

        print(
            f"   🎥 Creating video: "
            f"{self.format_duration(duration)}"
        )
        print(
            f"   📹 Footage: {footage_path}"
        )
        print(
            f"   🎵 Audio: {start_sec}s → {end_sec}s"
        )

        try:
            cmd = [
                "ffmpeg",
                "-y",

                # ── Video Input (loop forever) ──
                "-stream_loop", "-1",
                "-i", footage_path,

                # ── Audio Input (with offset) ──
                "-ss", str(int(start_sec)),
                "-t",  str(int(duration)),
                "-i",  audio_path,

                # ── Stream Mapping ──
                "-map", "0:v:0",
                "-map", "1:a:0",

                # ── Video Settings ──
                "-c:v",    "libx264",
                "-preset", "ultrafast",
                "-crf",    "28",
                "-vf", (
                    "scale=1920:1080:"
                    "force_original_aspect_ratio=increase,"
                    "crop=1920:1080"
                ),
                "-r", "30",

                # ── Audio Settings ──
                "-c:a",  "aac",
                "-b:a",  "128k",
                "-ar",   "44100",

                # ── Duration Control ──
                "-t",       str(int(duration)),
                "-shortest",

                # ── No subtitles ──
                "-sn",

                output_path
            ]

            print("   ⚙️ Running FFmpeg...")

            result = subprocess.run(
                cmd,
                capture_output = True,
                text           = True,
                timeout        = 7200  # 2hr timeout
            )

            if result.returncode == 0:
                if os.path.exists(output_path):
                    size = os.path.getsize(output_path)
                    print(
                        f"   ✅ Video ready: "
                        f"{size // 1024 // 1024} MB"
                    )
                    return output_path
                else:
                    print("   ❌ Output file missing")
                    return None
            else:
                print(
                    f"   ❌ FFmpeg failed:\n"
                    f"   {result.stderr[-300:]}"
                )
                return None

        except subprocess.TimeoutExpired:
            print("   ❌ FFmpeg timeout (2 hours)")
            return None
        except Exception as e:
            print(f"   ❌ Video error: {e}")
            return None