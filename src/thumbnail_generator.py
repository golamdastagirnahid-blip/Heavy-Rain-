"""
Thumbnail Generator
Extracts random frame from stock footage
Adds professional text overlay
Looks cinematic and real
"""

import os
import random
import subprocess
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter
)


THUMB_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "thumbnails"
)

os.makedirs(THUMB_DIR, exist_ok=True)


class ThumbnailGenerator:

    def generate(
        self,
        title,
        footage_path,
        part_num=None,
        total_parts=None,
        duration_str=""
    ):
        """
        Generate thumbnail from real footage frame
        Adds professional text overlay
        Returns thumbnail file path
        """
        print("   🖼️ Generating thumbnail...")

        output_path = os.path.join(
            THUMB_DIR,
            f"thumb_{part_num or 1}.jpg"
        )

        # Step 1: Get footage duration
        footage_duration = self._get_duration(
            footage_path
        )

        if footage_duration == 0:
            print(
                "   ⚠️ Could not get footage duration"
            )
            footage_duration = 30

        # Step 2: Pick random timestamp
        # Between 20% and 80% to avoid
        # black frames at start/end
        min_time = footage_duration * 0.20
        max_time = footage_duration * 0.80
        timestamp = random.uniform(min_time, max_time)

        print(
            f"   📸 Extracting frame at "
            f"{timestamp:.1f}s"
        )

        # Step 3: Extract frame using FFmpeg
        frame_path = os.path.join(
            THUMB_DIR,
            f"frame_{part_num or 1}.jpg"
        )

        frame = self._extract_frame(
            footage_path,
            timestamp,
            frame_path
        )

        if not frame:
            print(
                "   ⚠️ Frame extraction failed"
                " - using solid background"
            )
            frame = self._create_fallback(frame_path)

        # Step 4: Add professional overlay
        result = self._add_overlay(
            frame_path   = frame,
            output_path  = output_path,
            title        = title,
            part_num     = part_num,
            total_parts  = total_parts,
            duration_str = duration_str
        )

        if result:
            print(f"   ✅ Thumbnail ready: {result}")
            return result

        print("   ❌ Thumbnail generation failed")
        return None

    def _get_duration(self, file_path):
        """Get video duration in seconds"""
        try:
            cmd = [
                "ffprobe",
                "-v",            "quiet",
                "-print_format", "json",
                "-show_format",
                file_path
            ]
            result = subprocess.run(
                cmd,
                capture_output = True,
                text           = True,
                timeout        = 30
            )
            import json
            data = json.loads(result.stdout)
            return float(
                data["format"]["duration"]
            )
        except Exception as e:
            print(f"   ⚠️ Duration error: {e}")
            return 0

    def _extract_frame(
        self,
        footage_path,
        timestamp,
        output_path
    ):
        """Extract single frame from video"""
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-ss",     str(timestamp),
                "-i",      footage_path,
                "-vframes","1",
                "-vf",     "scale=1280:720",
                "-q:v",    "2",
                output_path
            ]

            result = subprocess.run(
                cmd,
                capture_output = True,
                text           = True,
                timeout        = 30
            )

            if (
                result.returncode == 0
                and os.path.exists(output_path)
            ):
                return output_path

            print(
                f"   ⚠️ FFmpeg frame error: "
                f"{result.stderr[-100:]}"
            )
            return None

        except Exception as e:
            print(f"   ⚠️ Frame extract error: {e}")
            return None

    def _create_fallback(self, output_path):
        """
        Create dark rain-themed background
        if frame extraction fails
        """
        try:
            img  = Image.new(
                "RGB",
                (1280, 720),
                (15, 25, 45)
            )
            draw = ImageDraw.Draw(img)

            # Draw simple rain lines
            for _ in range(300):
                x  = random.randint(0, 1280)
                y  = random.randint(0, 720)
                y2 = y + random.randint(15, 50)
                draw.line(
                    [(x, y), (x+1, y2)],
                    fill  = (80, 120, 180),
                    width = 1
                )

            img.save(output_path, "JPEG", quality=95)
            return output_path

        except Exception as e:
            print(f"   ⚠️ Fallback error: {e}")
            return None

    def _add_overlay(
        self,
        frame_path,
        output_path,
        title,
        part_num=None,
        total_parts=None,
        duration_str=""
    ):
        """
        Add professional text overlay to frame
        Dark gradient at bottom
        Clean minimal typography
        """
        try:
            # Open the frame
            img = Image.open(frame_path).convert("RGB")
            img = img.resize(
                (1280, 720),
                Image.LANCZOS
            )

            # Create overlay layer
            overlay = Image.new(
                "RGBA",
                (1280, 720),
                (0, 0, 0, 0)
            )
            draw = ImageDraw.Draw(overlay)

            # ── Dark gradient at bottom ──
            # Gets darker towards bottom
            for i in range(380):
                # Alpha increases towards bottom
                alpha = int((i / 380) * 210)
                draw.rectangle(
                    [
                        (0,    340 + i),
                        (1280, 341 + i)
                    ],
                    fill=(0, 0, 0, alpha)
                )

            # ── Dark vignette on sides ──
            for i in range(200):
                alpha = int((1 - i/200) * 80)
                # Left side
                draw.rectangle(
                    [(i, 0), (i+1, 720)],
                    fill=(0, 0, 0, alpha)
                )
                # Right side
                draw.rectangle(
                    [(1279-i, 0), (1280-i, 720)],
                    fill=(0, 0, 0, alpha)
                )

            # Merge overlay with image
            img = img.convert("RGBA")
            img = Image.alpha_composite(img, overlay)
            img = img.convert("RGB")

            draw = ImageDraw.Draw(img)

            # ── Load Fonts ──
            font_title   = self._get_font(72)
            font_sub     = self._get_font(36)
            font_small   = self._get_font(28)
            font_channel = self._get_font(24)

            # ── Channel Name (top left) ──
            draw.text(
                (40, 35),
                "🌧️ Heavy Rain Deep Sleep",
                font = font_channel,
                fill = (180, 210, 255)
            )

            # ── Blue accent line ──
            draw.rectangle(
                [(40, 68), (340, 72)],
                fill=(70, 130, 220)
            )

            # ── Title Text ──
            # Clean and wrap title
            clean_title = title.replace(
                "| Part", ""
            ).strip()

            # Wrap title into max 2 lines
            words  = clean_title.split()
            lines  = []
            line   = ""

            for word in words:
                test = f"{line} {word}".strip()
                if len(test) <= 30:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = word

            if line:
                lines.append(line)

            lines = lines[:2]  # Max 2 lines

            # Draw title with shadow
            title_y = 480 if len(lines) > 1 else 510

            for line in lines:
                # Shadow
                draw.text(
                    (44, title_y + 4),
                    line,
                    font = font_title,
                    fill = (0, 0, 0, 180)
                )
                # Main text
                draw.text(
                    (40, title_y),
                    line,
                    font = font_title,
                    fill = (255, 255, 255)
                )
                title_y += 82

            # ── Bottom info bar ──
            bar_y = 640

            # Duration badge
            if duration_str:
                # Badge background
                draw.rounded_rectangle(
                    [(40, bar_y), (200, bar_y+42)],
                    radius = 8,
                    fill   = (70, 130, 220)
                )
                draw.text(
                    (55, bar_y + 8),
                    f"⏱ {duration_str}",
                    font = font_small,
                    fill = (255, 255, 255)
                )

            # No Ads badge
            draw.rounded_rectangle(
                [(215, bar_y), (330, bar_y+42)],
                radius = 8,
                fill   = (40, 160, 80)
            )
            draw.text(
                (230, bar_y + 8),
                "✅ No Ads",
                font = font_small,
                fill = (255, 255, 255)
            )

            # Sleep badge
            draw.rounded_rectangle(
                [(345, bar_y), (500, bar_y+42)],
                radius = 8,
                fill   = (100, 60, 180)
            )
            draw.text(
                (360, bar_y + 8),
                "😴 Deep Sleep",
                font = font_small,
                fill = (255, 255, 255)
            )

            # ── Part number (if multiple parts) ──
            if (
                part_num
                and total_parts
                and total_parts > 1
            ):
                draw.text(
                    (40, bar_y - 45),
                    f"Part {part_num} of {total_parts}",
                    font = font_sub,
                    fill = (180, 210, 255)
                )

            # ── Rain emoji accents ──
            draw.text(
                (1200, 35),
                "🌧️",
                font = self._get_font(48),
                fill = (255, 255, 255)
            )

            # Save final thumbnail
            img.save(
                output_path,
                "JPEG",
                quality = 95
            )

            return output_path

        except Exception as e:
            print(f"   ⚠️ Overlay error: {e}")
            return None

    def _get_font(self, size):
        """
        Load font - tries multiple paths
        Falls back to default if not found
        """
        font_paths = [
            # Ubuntu/Debian
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            # Generic
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue

        # Fallback to default
        return ImageFont.load_default()
