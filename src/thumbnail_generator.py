"""
Thumbnail Generator
Real footage screenshot visible through overlay
Transparent cinematic overlay
Professional text on top
"""

import os
import re
import json
import random
import subprocess
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageEnhance,
)

THUMB_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "thumbnails"
)
os.makedirs(THUMB_DIR, exist_ok=True)

# Colors from HTML preview
BLUE   = (65,  145, 255)
WHITE  = (240, 245, 255)
SHADOW = (0,   5,   16)


class ThumbnailGenerator:

    def generate(
        self,
        title,
        footage_path = None,
        part_num     = None,
        total_parts  = None,
        duration_str = ""
    ):
        print("   🖼️ Generating thumbnail...")

        output_path = os.path.join(
            THUMB_DIR,
            f"thumb_{part_num or 1}.jpg"
        )
        frame_path = os.path.join(
            THUMB_DIR,
            f"frame_{part_num or 1}.jpg"
        )

        # Step 1: Extract REAL frame from footage
        bg = None
        if footage_path and os.path.exists(
            footage_path
        ):
            bg = self._extract_frame(
                footage_path, frame_path
            )

        if not bg:
            bg = self._fallback_bg(frame_path)

        # Step 2: Build thumbnail
        result = self._build(
            bg_path      = bg,
            output_path  = output_path,
            title        = title,
            part_num     = part_num,
            total_parts  = total_parts,
            duration_str = duration_str
        )

        if result:
            size = os.path.getsize(result)
            print(
                f"   ✅ Thumbnail: "
                f"{size // 1024} KB"
            )
            return result

        print("   ❌ Thumbnail failed")
        return None

    def _extract_frame(
        self, footage_path, frame_path
    ):
        """
        Extract REAL screenshot from footage
        High quality frame extraction
        """
        if not footage_path:
            return None
        if not os.path.exists(footage_path):
            return None

        try:
            # Get duration
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", footage_path
            ]
            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            d   = json.loads(r.stdout)
            dur = float(d["format"]["duration"])

            # Pick best frame 20%-80%
            ts = random.uniform(
                dur * 0.2, dur * 0.8
            )

            print(
                f"   📸 Screenshot at {ts:.1f}s"
            )

            # Extract at highest quality
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(ts),
                "-i", footage_path,
                "-vframes", "1",
                "-vf", (
                    "scale=1280:720:"
                    "force_original_aspect_ratio"
                    "=increase,"
                    "crop=1280:720"
                ),
                "-q:v", "1",
                frame_path
            ]
            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if (
                r.returncode == 0
                and os.path.exists(frame_path)
                and os.path.getsize(frame_path) > 1024
            ):
                print(
                    f"   ✅ Frame: "
                    f"{os.path.getsize(frame_path)//1024}KB"
                )
                return frame_path

        except Exception as e:
            print(f"   ⚠️ Frame error: {e}")

        return None

    def _fallback_bg(self, output_path):
        """Dark rain background if no footage"""
        try:
            img  = Image.new(
                "RGB", (1280, 720), (10, 22, 40)
            )
            draw = ImageDraw.Draw(img)

            for _ in range(400):
                x = random.randint(0, 1280)
                y = random.randint(0, 720)
                h = random.randint(30, 80)
                o = random.uniform(0.2, 0.6)
                draw.line(
                    [(x, y), (x+1, y+h)],
                    fill=(
                        int(80*o),
                        int(130*o),
                        int(200*o)
                    ),
                    width=1
                )

            img.save(output_path, "JPEG", quality=98)
            return output_path
        except Exception:
            return None

    def _build(
        self,
        bg_path,
        output_path,
        title,
        part_num     = None,
        total_parts  = None,
        duration_str = ""
    ):
        """
        Build thumbnail with transparent overlay
        Real footage visible through gradient
        """
        try:
            W, H = 1280, 720
            S    = 2  # Scale from 640→1280

            PAD_X = 28 * S  # 56px
            PAD_Y = 20 * S  # 40px

            # ════════════════════════════
            # STEP 1: Load real footage frame
            # ════════════════════════════
            img = Image.open(
                bg_path
            ).convert("RGB")
            img = img.resize(
                (W, H), Image.LANCZOS
            )

            # ════════════════════════════
            # STEP 2: Light color grading
            # Keep image VISIBLE
            # Only slight darkening
            # ════════════════════════════

            # Slight darken (90% brightness)
            # NOT too dark - footage must be visible
            img = ImageEnhance.Brightness(
                img
            ).enhance(0.90)

            # Slight contrast boost
            img = ImageEnhance.Contrast(
                img
            ).enhance(1.15)

            # Slight blue tint for rain mood
            r, g, b = img.split()
            b = ImageEnhance.Brightness(
                b
            ).enhance(1.10)
            img = Image.merge("RGB", (r, g, b))

            # ════════════════════════════
            # STEP 3: Light transparent overlay
            # Bottom only - keep top CLEAR
            # Real footage visible everywhere
            # ════════════════════════════

            img  = img.convert("RGBA")
            over = Image.new(
                "RGBA", (W, H), (0, 0, 0, 0)
            )
            draw = ImageDraw.Draw(over)

            # Bottom gradient - ONLY bottom 45%
            # Very transparent at top of gradient
            # Darker at very bottom for text readability
            bot_start = int(H * 0.55)  # Start at 55%
            bot_h     = H - bot_start  # 45% height

            for i in range(bot_h):
                t = i / bot_h
                # Smooth curve - transparent→dark
                alpha = int((t ** 2.0) * 200)
                draw.rectangle(
                    [
                        (0,   bot_start + i),
                        (W-1, bot_start + i + 1)
                    ],
                    fill=(5, 10, 25, alpha)
                )

            # Top gradient - VERY light
            # Just subtle darkening for channel name
            top_h = int(H * 0.15)  # Only 15%
            for i in range(top_h):
                t = 1 - (i / top_h)
                alpha = int(t * 60)  # Max 60 opacity
                draw.rectangle(
                    [(0, i), (W-1, i+1)],
                    fill=(5, 10, 25, alpha)
                )

            # NO side vignettes
            # Keep image fully visible

            # Merge overlay
            img = Image.alpha_composite(img, over)
            img = img.convert("RGB")
            draw = ImageDraw.Draw(img)

            # ════════════════════════════
            # STEP 4: Load fonts
            # ════════════════════════════
            f_chan  = self._font(11 * S)   # 22px
            f_part  = self._font(14 * S)   # 28px
            f_title = self._font(38 * S)   # 76px
            f_badge = self._font(12 * S)   # 24px

            # ════════════════════════════
            # STEP 5: Top section
            # Channel branding
            # ════════════════════════════

            top_y = PAD_Y

            # Blue bar
            draw.rectangle(
                [
                    (PAD_X,     top_y),
                    (PAD_X + 6, top_y + 52)
                ],
                fill=BLUE
            )

            # Channel name with strong shadow
            chan_x = PAD_X + 22
            chan_y = top_y + 8
            chan_text = "HEAVY RAIN DEEP SLEEP"

            # Strong shadow for readability
            for ox, oy in [
                (2, 2), (3, 3), (1, 3), (3, 1)
            ]:
                draw.text(
                    (chan_x + ox, chan_y + oy),
                    chan_text,
                    font=f_chan,
                    fill=(0, 0, 0)
                )
            draw.text(
                (chan_x, chan_y),
                chan_text,
                font=f_chan,
                fill=BLUE
            )

            # Rain emoji top right
            try:
                bbox = draw.textbbox(
                    (0, 0), "🌧", font=self._font(52)
                )
                iw   = bbox[2] - bbox[0]
                draw.text(
                    (W - PAD_X - iw, top_y),
                    "🌧",
                    font=self._font(52),
                    fill=WHITE
                )
            except Exception:
                pass

            # ════════════════════════════
            # STEP 6: Badges at bottom
            # ════════════════════════════

            badge_colors = [
                (37,  99,  235),  # Duration blue
                (22,  163,  74),  # No Ads green
                (124,  58, 237),  # Sleep purple
                (220,  38,  38),  # HD red
            ]

            # Measure badge height
            bb  = draw.textbbox(
                (0, 0), "TEST", font=f_badge
            )
            bth = bb[3] - bb[1]
            bh  = bth + 16  # padding
            bpy = 8         # text pad y

            badge_y = H - PAD_Y - bh
            badge_x = PAD_X

            badge_data = []
            if duration_str:
                badge_data.append(
                    (f"  {duration_str.upper()}  ",
                     badge_colors[0])
                )
            badge_data.append(
                ("  NO ADS  ", badge_colors[1])
            )
            badge_data.append(
                ("  SLEEP AID  ", badge_colors[2])
            )
            badge_data.append(
                ("  HD  ", badge_colors[3])
            )

            for btext, bcolor in badge_data:
                try:
                    tb = draw.textbbox(
                        (0, 0), btext, font=f_badge
                    )
                    tw = tb[2] - tb[0]
                except Exception:
                    tw = len(btext) * 14

                bw = tw + 10

                # Badge shadow
                draw.rounded_rectangle(
                    [
                        (badge_x + 3, badge_y + 3),
                        (badge_x + bw + 3,
                         badge_y + bh + 3)
                    ],
                    radius=10,
                    fill=(0, 0, 0, 150)
                )

                # Badge background
                draw.rounded_rectangle(
                    [
                        (badge_x,      badge_y),
                        (badge_x + bw, badge_y + bh)
                    ],
                    radius=10,
                    fill=bcolor
                )

                # Badge text
                draw.text(
                    (badge_x + 5, badge_y + bpy),
                    btext,
                    font=f_badge,
                    fill=(255, 255, 255)
                )

                badge_x += bw + 12

            # ════════════════════════════
            # STEP 7: Title text
            # Big bold text at bottom
            # With strong shadow for
            # readability over footage
            # ════════════════════════════

            # Clean title
            clean = title
            if part_num:
                clean = re.sub(
                    r'\s*\|\s*Part\s*\d+.*$',
                    '', clean,
                    flags=re.IGNORECASE
                ).strip()

            clean = re.sub(
                r'[^\x00-\x7F]+', '', clean
            ).strip().upper()

            if not clean:
                clean = "HEAVY RAIN SOUNDS"

            # Word wrap 20 chars per line
            words = clean.split()
            lines = []
            line  = ""
            for w in words:
                test = (line + " " + w).strip()
                if len(test) <= 20:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = w
            if line:
                lines.append(line)
            lines = lines[:2]

            # Line height
            lh = int(38 * S * 1.1)  # 84px

            # Position title above badges
            title_total = len(lines) * lh
            title_y = badge_y - 20 - title_total

            for ln in lines:
                # Strong black shadow
                # Multiple layers for readability
                # over footage
                for ox, oy in [
                    (4, 4), (5, 5), (6, 6),
                    (3, 5), (5, 3),
                    (3, 3), (4, 5), (5, 4),
                ]:
                    draw.text(
                        (PAD_X + ox, title_y + oy),
                        ln,
                        font=f_title,
                        fill=(0, 0, 10)
                    )

                # Blue glow outline
                for ox, oy in [
                    (-2, 0), (2, 0),
                    (0, -2), (0, 2),
                    (-2, -2), (2, 2),
                    (-2, 2), (2, -2),
                ]:
                    draw.text(
                        (PAD_X + ox, title_y + oy),
                        ln,
                        font=f_title,
                        fill=(30, 80, 180)
                    )

                # White main text
                draw.text(
                    (PAD_X, title_y),
                    ln,
                    font=f_title,
                    fill=(255, 255, 255)
                )

                title_y += lh

            # ════════════════════════════
            # STEP 8: Part indicator
            # ════════════════════════════
            if (
                part_num
                and total_parts
                and total_parts > 1
            ):
                pt = (
                    f"PART {part_num} "
                    f"OF {total_parts}"
                )
                py = (
                    badge_y - 20 -
                    title_total - 40
                )

                # Shadow
                for ox, oy in [
                    (2, 2), (3, 3), (2, 3)
                ]:
                    draw.text(
                        (PAD_X + ox, py + oy),
                        pt,
                        font=f_part,
                        fill=(0, 0, 10)
                    )

                draw.text(
                    (PAD_X, py),
                    pt,
                    font=f_part,
                    fill=BLUE
                )

            # ════════════════════════════
            # STEP 9: Save
            # ════════════════════════════
            img.save(
                output_path,
                "JPEG",
                quality=98,
                subsampling=0
            )
            return output_path

        except Exception as e:
            print(f"   ❌ Build error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _font(self, size):
        """Load best bold font"""
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for path in paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(
                        path, size
                    )
                except Exception:
                    continue
        return ImageFont.load_default()
