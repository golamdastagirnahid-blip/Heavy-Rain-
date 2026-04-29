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

# GitHub Actions max runtime = 6 hours
# FFmpeg gets max 5 hours safe limit
GITHUB_SAFE_TIMEOUT = 5 * 60 * 60


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

    def _calculate_timeout(self, duration_seconds):
        """
        Calculate safe FFmpeg timeout
        GitHub Actions limit = 6 hours total
        FFmpeg gets max 5 hours safe limit
        Rule: 1.5x video duration
        """
        timeout = int(duration_seconds * 1.5)
        timeout = min(timeout, GITHUB_SAFE_TIMEOUT)
        timeout = max(timeout, 1800)

        hours = timeout // 3600
        mins  = (timeout % 3600) // 60
        print(
            f"   ⏱️  FFmpeg timeout: "
            f"{hours}h {mins}m "
            f"(GitHub limit: 6h total)"
        )
        return timeout

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
        - Scales to 1280x720
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
        print(f"   📹 Footage: {footage_path}")
        print(
            f"   🎵 Audio: "
            f"{start_sec}s → {end_sec}s"
        )

        # ── Validate inputs ──
        if not os.path.exists(footage_path):
            print(
                f"   ❌ Footage not found: "
                f"{footage_path}"
            )
            return None

        if not os.path.exists(audio_path):
            print(
                f"   ❌ Audio not found: "
                f"{audio_path}"
            )
            return None

        if duration <= 0:
            print(
                f"   ❌ Invalid duration: "
                f"{duration}s"
            )
            return None

        try:
            timeout = self._calculate_timeout(
                duration
            )

            cmd = [
                "ffmpeg",
                "-y",

                # ── Video input (loop forever) ──
                "-stream_loop", "-1",
                "-i", footage_path,

                # ── Audio input (with offset) ──
                "-ss", str(int(start_sec)),
                "-t",  str(int(duration)),
                "-i",  audio_path,

                # ── Stream mapping ──
                "-map", "0:v:0",
                "-map", "1:a:0",

                # ── Video settings ──
                # ultrafast = fastest encode
                # crf 35    = good enough for sleep
                # threads 0 = use all CPU cores
                "-c:v",     "libx264",
                "-preset",  "ultrafast",
                "-crf",     "35",
                "-tune",    "fastdecode",
                "-threads", "0",

                # 720p = 56% fewer pixels than 1080p
                # Much faster + fine for sleep videos
                "-vf", (
                    "scale=1280:720:"
                    "force_original_aspect_ratio=increase,"
                    "crop=1280:720"
                ),

                # 24fps saves ~20% vs 30fps
                "-r", "24",

                # ── Audio settings ──
                "-c:a", "aac",
                "-b:a", "128k",
                "-ar",  "44100",

                # ── Duration control ──
                "-t",       str(int(duration)),
                "-shortest",

                # ── Extra flags ──
                "-sn",                     # no subtitles
                "-movflags", "+faststart", # web playback

                # ── Logging ──
                "-stats",
                "-loglevel", "warning",

                output_path
            ]

            est_mins = int(duration * 0.3 / 60)
            print(
                f"   ⚙️ Running FFmpeg...\n"
                f"   📐 720p/24fps/crf35/ultrafast\n"
                f"   ⏳ Estimated: ~{est_mins} mins"
            )

            result = subprocess.run(
                cmd,
                capture_output = True,
                text           = True,
                timeout        = timeout
            )

            if result.returncode == 0:
                if os.path.exists(output_path):
                    size    = os.path.getsize(
                        output_path
                    )
                    size_mb = size // 1024 // 1024
                    print(
                        f"   ✅ Video ready: "
                        f"{size_mb} MB"
                    )
                    return output_path
                else:
                    print(
                        "   ❌ Output file missing"
                    )
                    return None
            else:
                err = result.stderr[-500:] \
                    if result.stderr else "none"
                print(
                    f"   ❌ FFmpeg failed "
                    f"(code {result.returncode}):\n"
                    f"   {err}"
                )
                return None

        except subprocess.TimeoutExpired:
            timeout_h = timeout // 3600
            print(
                f"   ❌ FFmpeg exceeded "
                f"{timeout_h}h GitHub safe limit"
            )
            return None

        except Exception as e:
            print(f"   ❌ Video error: {e}")
            import traceback
            traceback.print_exc()
            return None
