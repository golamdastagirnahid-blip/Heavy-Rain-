"""
Video Processor
720p output - faster processing
No thumbnail embedding
Optimized FFmpeg settings
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
        thumbnail_path = None  # Not used anymore
    ):
        """
        Create 720p video by looping footage
        over audio segment
        Fastest possible settings
        No thumbnail embedding
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
        print(f"   📹 Footage : {footage_path}")
        print(
            f"   🎵 Audio   : "
            f"{self.format_duration(start_sec)}"
            f" → "
            f"{self.format_duration(end_sec)}"
        )
        print(f"   📐 Quality : 720p")
        print(f"   ⚡ Preset  : ultrafast")

        try:
            cmd = [
                "ffmpeg",
                "-y",

                # ── Video input loop forever ──
                "-stream_loop", "-1",
                "-i", footage_path,

                # ── Audio input with offset ──
                "-ss", str(int(start_sec)),
                "-t",  str(int(duration)),
                "-i",  audio_path,

                # ── Map streams ──
                "-map", "0:v:0",
                "-map", "1:a:0",

                # ── Video: 720p ultrafast ──
                "-c:v",    "libx264",
                "-preset", "ultrafast",
                "-tune",   "fastdecode",
                "-crf",    "30",
                "-vf", (
                    "scale=1280:720:"
                    "force_original_aspect_ratio=increase,"
                    "crop=1280:720,"
                    "fps=24"
                ),
                "-profile:v", "baseline",
                "-level",     "3.1",

                # ── Audio: efficient ──
                "-c:a",  "aac",
                "-b:a",  "96k",
                "-ar",   "44100",
                "-ac",   "2",

                # ── Duration control ──
                "-t",       str(int(duration)),
                "-shortest",

                # ── No subtitles ──
                "-sn",

                # ── No metadata ──
                "-map_metadata", "-1",

                # ── Threading ──
                "-threads", "0",

                output_path
            ]

            print("   ⚙️ Running FFmpeg...")

            result = subprocess.run(
                cmd,
                capture_output = True,
                text           = True,
                timeout        = 14400  # 4 hours
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
                else:
                    print(
                        "   ❌ Output file missing"
                    )
                    return None
            else:
                print(
                    f"   ❌ FFmpeg failed:\n"
                    f"   {result.stderr[-300:]}"
                )
                return None

        except subprocess.TimeoutExpired:
            print("   ❌ FFmpeg timeout (4 hours)")
            return None
        except Exception as e:
            print(f"   ❌ Video error: {e}")
            return None
