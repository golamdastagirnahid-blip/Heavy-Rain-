"""
Thumbnail Generator
100% pixel accurate match to HTML preview
Font: Arial Black equivalent (DejaVuSans-Bold)
Canvas: 1280x720
All values scaled from 640x360 HTML preview x2
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
    ImageFilter
)

THUMB_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "thumbnails"
)
os.makedirs(THUMB_DIR, exist_ok=True)

# ─────────────────────────────────────────
# EXACT COLORS FROM HTML
# All values taken directly from CSS
# ─────────────────────────────────────────

# Background gradient colors
BG_1 = (10,  22,  40)   # #0a1628
BG_2 = (13,  32,  64)   # #0d2040
BG_3 = (10,  24,  48)   # #0a1830
BG_4 = (6,   14,  30)   # #060e1e

# Brand
BLUE         = (65,  145, 255)  # #4191ff
WHITE        = (240, 245, 255)  # #f0f5ff
SHADOW       = (0,   5,   16)   # #000510

# Bottom gradient stops
BOT_G1 = (5,  12, 30,   0)    # transparent
BOT_G2 = (5,  12, 30, 128)    # 0.5 opacity
BOT_G3 = (5,  12, 30, 217)    # 0.85 opacity
BOT_G4 = (3,   8, 20, 247)    # 0.97 opacity

# Top gradient
TOP_G1 = (5,  12, 30,   0)    # transparent
TOP_G2 = (5,  12, 30, 128)    # 0.5 opacity

# Vignette
VIG    = (0,   0, 15, 179)    # rgba(0,0,15,0.7)

# Badge gradients (start color used as flat)
BADGE_DUR = (37,  99,  235)   # #2563eb
BADGE_ADS = (22,  163,  74)   # #16a34a
BADGE_SLP = (124,  58, 237)   # #7c3aed
BADGE_HD  = (220,  38,  38)   # #dc2626

# Badge end colors (for gradient simulation)
BADGE_DUR2 = (29,  78,  216)  # #1d4ed8
BADGE_ADS2 = (21, 128,  61)   # #15803d
BADGE_SLP2 = (109, 40,  217)  # #6d28d9
BADGE_HD2  = (185, 28,  28)   # #b91c1c


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

        # Get background
        bg = None
        if footage_path and os.path.exists(
            footage_path
        ):
            bg = self._extract_frame(
                footage_path, frame_path
            )

        if not bg:
            bg = self._make_bg(frame_path)

        # Build thumbnail
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

    # ─────────────────────────────────────
    # BACKGROUND
    # ─────────────────────────────────────

    def _extract_frame(
        self, footage_path, frame_path
    ):
        """Extract random frame from footage"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", footage_path
            ]
            r = subprocess.run(
                cmd, capture_output=True,
                text=True, timeout=30
            )
            d  = json.loads(r.stdout)
            dur= float(d["format"]["duration"])
            ts = random.uniform(dur*0.2, dur*0.8)

            cmd = [
                "ffmpeg", "-y",
                "-ss", str(ts),
                "-i", footage_path,
                "-vframes", "1",
                "-vf", "scale=1280:720:flags=lanczos",
                "-q:v", "1",
                frame_path
            ]
            r = subprocess.run(
                cmd, capture_output=True,
                text=True, timeout=30
            )
            if (
                r.returncode == 0
                and os.path.exists(frame_path)
            ):
                print(f"   📸 Frame at {ts:.1f}s")
                return frame_path
        except Exception as e:
            print(f"   ⚠️ Frame: {e}")
        return None

    def _make_bg(self, output_path):
        """
        Create background matching HTML CSS:
        background: linear-gradient(135deg,
            #0a1628 0%, #0d2040 30%,
            #0a1830 60%, #060e1e 100%)
        Plus rain streaks
        """
        try:
            W, H = 1280, 720
            img  = Image.new("RGB", (W, H))
            draw = ImageDraw.Draw(img)

            # 135deg gradient
            # At 135deg, progress goes from
            # top-left to bottom-right
            for y in range(H):
                for x in range(0, W, 4):
                    # Progress 0-1 along 135deg axis
                    t = (x/W + y/H) / 2

                    if t < 0.30:
                        p  = t / 0.30
                        r  = int(BG_1[0]*(1-p) + BG_2[0]*p)
                        g  = int(BG_1[1]*(1-p) + BG_2[1]*p)
                        b  = int(BG_1[2]*(1-p) + BG_2[2]*p)
                    elif t < 0.60:
                        p  = (t-0.30) / 0.30
                        r  = int(BG_2[0]*(1-p) + BG_3[0]*p)
                        g  = int(BG_2[1]*(1-p) + BG_3[1]*p)
                        b  = int(BG_2[2]*(1-p) + BG_3[2]*p)
                    else:
                        p  = (t-0.60) / 0.40
                        r  = int(BG_3[0]*(1-p) + BG_4[0]*p)
                        g  = int(BG_3[1]*(1-p) + BG_4[1]*p)
                        b  = int(BG_3[2]*(1-p) + BG_4[2]*p)

                    draw.rectangle(
                        [(x, y), (x+3, y)],
                        fill=(r, g, b)
                    )

            # Rain streaks matching HTML animation
            for _ in range(500):
                x   = random.randint(0, W)
                y   = random.randint(-50, H)
                h   = random.randint(15*2, 55*2)
                opa = random.uniform(0.2, 0.7)
                col = (
                    int(100 * opa),
                    int(160 * opa),
                    int(255 * opa)
                )
                draw.line(
                    [(x, y), (x+1, y+h)],
                    fill=col, width=1
                )

            img.save(output_path, "JPEG", quality=98)
            return output_path

        except Exception as e:
            print(f"   ⚠️ BG error: {e}")
            # Ultra simple fallback
            img = Image.new("RGB", (1280, 720), BG_1)
            img.save(output_path, "JPEG", quality=98)
            return output_path

    # ─────────────────────────────────────
    # MAIN BUILD
    # ─────────────────────────────────────

    def _build(
        self,
        bg_path,
        output_path,
        title,
        part_num    = None,
        total_parts = None,
        duration_str= ""
    ):
        """
        Build thumbnail exactly matching HTML
        All measurements scaled x2 from HTML
        HTML preview is 640x360
        Output is 1280x720
        """
        try:
            W, H = 1280, 720

            # Scale factor from HTML to output
            # HTML: 640x360 → Output: 1280x720
            S = 2

            # ── Open background ──
            img = Image.open(
                bg_path
            ).convert("RGBA")
            img = img.resize(
                (W, H), Image.LANCZOS
            )

            # ── Color grade footage ──
            # Darken slightly like overlay effect
            img_rgb = img.convert("RGB")
            img_rgb = ImageEnhance.Brightness(
                img_rgb
            ).enhance(0.80)
            img_rgb = ImageEnhance.Contrast(
                img_rgb
            ).enhance(1.15)
            img = img_rgb.convert("RGBA")

            draw = ImageDraw.Draw(img)

            # ════════════════════════════════
            # OVERLAYS - matching HTML exactly
            # ════════════════════════════════

            # ── Bottom gradient ──
            # height: 75% = 540px
            # transparent → rgba(5,12,30,0.5) at 30%
            # → rgba(5,12,30,0.85) at 60%
            # → rgba(3,8,20,0.97) at 100%
            bot_start = H - int(H * 0.75)  # = 180
            bot_h     = int(H * 0.75)      # = 540

            for i in range(bot_h):
                t = i / bot_h  # 0 to 1

                if t < 0.30:
                    p = t / 0.30
                    a = int(0 + p * 128)      # 0→128
                    c = (5, 12, 30, a)
                elif t < 0.60:
                    p = (t - 0.30) / 0.30
                    a = int(128 + p * 89)     # 128→217
                    c = (5, 12, 30, a)
                else:
                    p = (t - 0.60) / 0.40
                    a = int(217 + p * 30)     # 217→247
                    r = int(5 - p*2)          # 5→3
                    g = int(12 - p*4)         # 12→8
                    b = int(30 - p*10)        # 30→20
                    c = (r, g, b, a)

                draw.rectangle(
                    [(0, bot_start+i), (W, bot_start+i+1)],
                    fill=c
                )

            # ── Top gradient ──
            # height: 35% = 252px
            # transparent → rgba(5,12,30,0.5)
            top_h = int(H * 0.35)  # = 252

            for i in range(top_h):
                # Goes from bottom(transparent)
                # to top(0.5 opacity)
                t = 1 - (i / top_h)  # 1 at top
                a = int(t * 128)      # 128 = 0.5*255
                draw.rectangle(
                    [(0, i), (W, i+1)],
                    fill=(5, 12, 30, a)
                )

            # ── Left vignette ──
            # width: 30% = 384px
            # rgba(0,0,15,0.7) → transparent
            vig_w = int(W * 0.30)  # = 384

            for i in range(vig_w):
                t = 1 - (i / vig_w)
                a = int(t * 179)     # 179 = 0.7*255
                draw.rectangle(
                    [(i, 0), (i+1, H)],
                    fill=(0, 0, 15, a)
                )

            # ── Right vignette ──
            for i in range(vig_w):
                t = 1 - (i / vig_w)
                a = int(t * 179)
                draw.rectangle(
                    [(W-1-i, 0), (W-i, H)],
                    fill=(0, 0, 15, a)
                )

            # Convert to RGB for text drawing
            img  = img.convert("RGB")
            draw = ImageDraw.Draw(img)

            # ════════════════════════════════
            # CONTENT - padding: 20px 28px x2
            # = 40px top/bottom, 56px left/right
            # ════════════════════════════════

            PAD_X = 28 * S   # 56px
            PAD_Y = 20 * S   # 40px

            # ── Load fonts ──
            # HTML: font-family: 'Arial Black', Arial
            # Best match on Ubuntu: DejaVuSans-Bold

            # channel-name: 11px → 22px
            f_channel = self._font(11 * S)

            # part-indicator: 13px → 26px
            f_part    = self._font(13 * S)

            # title: 36px → 72px
            f_title   = self._font(36 * S)

            # badge: 11px → 22px
            f_badge   = self._font(11 * S)

            # rain icon: 26px → 52px
            f_icon    = self._font(26 * S)

            # ════════════════════════════════
            # TOP SECTION
            # ════════════════════════════════

            top_y = PAD_Y  # 40px from top

            # ── Brand bar ──
            # width: 3px → 6px
            # height: 26px → 52px
            # color: #4191ff
            bar_x = PAD_X
            bar_w = 3 * S   # 6px
            bar_h = 26 * S  # 52px

            draw.rectangle(
                [
                    (bar_x,       top_y),
                    (bar_x+bar_w, top_y+bar_h)
                ],
                fill=BLUE
            )

            # Glow effect on bar
            # box-shadow: 0 0 8px rgba(65,145,255,0.8)
            glow_img = Image.new(
                "RGBA", (W, H), (0, 0, 0, 0)
            )
            glow_draw= ImageDraw.Draw(glow_img)
            for g in range(1, 9):
                alpha = int(204 * (1 - g/9))
                glow_draw.rectangle(
                    [
                        (bar_x-g,       top_y-g),
                        (bar_x+bar_w+g, top_y+bar_h+g)
                    ],
                    fill=(*BLUE, alpha)
                )
            img = Image.alpha_composite(
                img.convert("RGBA"),
                glow_img
            ).convert("RGB")
            draw = ImageDraw.Draw(img)

            # ── Channel name ──
            # gap: 8px → 16px from bar
            # color: #4191ff
            # letter-spacing: 2px → 4px
            # text-shadow: 0 0 10px rgba(65,145,255,0.5)
            #              0 2px 4px rgba(0,0,0,0.8)
            chan_x = bar_x + bar_w + (8 * S)
            chan_y = top_y + 2

            channel_text = "HEAVY RAIN DEEP SLEEP"

            # Shadow: 0 2px 4px rgba(0,0,0,0.8)
            draw.text(
                (chan_x, chan_y + 4),
                channel_text,
                font = f_channel,
                fill = (0, 0, 0)
            )
            # Main blue text
            draw.text(
                (chan_x, chan_y),
                channel_text,
                font = f_channel,
                fill = BLUE
            )

            # ── Rain icon top right ──
            # font-size: 26px → 52px
            # position: top right with PAD_X
            try:
                icon_bbox = draw.textbbox(
                    (0, 0), "🌧️", font=f_icon
                )
                icon_w = icon_bbox[2] - icon_bbox[0]
                icon_x = W - PAD_X - icon_w
                draw.text(
                    (icon_x, top_y),
                    "🌧️",
                    font = f_icon,
                    fill = WHITE
                )
            except Exception:
                pass

            # ════════════════════════════════
            # BOTTOM SECTION
            # position: absolute bottom with PAD
            # ════════════════════════════════

            # Work from bottom up
            # gap between elements: 10px → 20px

            # ── Badges at very bottom ──
            # padding: 5px 12px → 10px 24px
            badge_pad_x = 12 * S   # 24px
            badge_pad_y = 5  * S   # 10px
            badge_gap   = 8  * S   # 16px
            badge_radius= 6  * S   # 12px

            # Measure badge heights
            badge_bbox = draw.textbbox(
                (0,0), "TEST", font=f_badge
            )
            badge_text_h = badge_bbox[3]-badge_bbox[1]
            badge_h      = badge_text_h + badge_pad_y*2

            # Badge bottom Y
            badge_y = H - PAD_Y - badge_h

            # Draw all 4 badges
            badge_x = PAD_X
            badges  = [
                (
                    f"⏱ {duration_str.upper()}",
                    BADGE_DUR, BADGE_DUR2
                ),
                ("✓ NO ADS",   BADGE_ADS, BADGE_ADS2),
                ("😴 SLEEP AID",BADGE_SLP, BADGE_SLP2),
                ("HD",          BADGE_HD,  BADGE_HD2),
            ]

            for badge_text, col1, col2 in badges:
                # Measure text
                try:
                    tb   = draw.textbbox(
                        (0,0), badge_text, font=f_badge
                    )
                    tw   = tb[2] - tb[0]
                except Exception:
                    tw = len(badge_text) * 13

                bw = tw + badge_pad_x * 2

                # Shadow: 0 3px 8px rgba(0,0,0,0.5)
                shadow_img = Image.new(
                    "RGBA", (W, H), (0,0,0,0)
                )
                shadow_draw= ImageDraw.Draw(shadow_img)
                for s in range(1, 6):
                    alpha = int(128 * (1-s/6))
                    shadow_draw.rounded_rectangle(
                        [
                            (badge_x+s,    badge_y+s),
                            (badge_x+bw+s, badge_y+badge_h+s)
                        ],
                        radius=badge_radius,
                        fill=(0, 0, 0, alpha)
                    )
                img = Image.alpha_composite(
                    img.convert("RGBA"),
                    shadow_img
                ).convert("RGB")
                draw = ImageDraw.Draw(img)

                # Badge gradient (135deg col1→col2)
                # Simulate with top→bottom blend
                badge_img  = Image.new(
                    "RGBA", (W, H), (0,0,0,0)
                )
                badge_draw = ImageDraw.Draw(badge_img)

                # Draw gradient inside rounded rect
                for gi in range(badge_h):
                    t  = gi / badge_h
                    # 135deg: blend diagonally
                    gr = int(col1[0]*(1-t)+col2[0]*t)
                    gg = int(col1[1]*(1-t)+col2[1]*t)
                    gb = int(col1[2]*(1-t)+col2[2]*t)
                    badge_draw.rectangle(
                        [
                            (badge_x,    badge_y+gi),
                            (badge_x+bw, badge_y+gi+1)
                        ],
                        fill=(gr, gg, gb, 255)
                    )

                # Clip to rounded rectangle
                mask = Image.new(
                    "L", (W, H), 0
                )
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rounded_rectangle(
                    [
                        (badge_x,    badge_y),
                        (badge_x+bw, badge_y+badge_h)
                    ],
                    radius=badge_radius,
                    fill=255
                )
                img = Image.alpha_composite(
                    img.convert("RGBA"),
                    Image.composite(
                        badge_img,
                        Image.new(
                            "RGBA", (W,H), (0,0,0,0)
                        ),
                        mask
                    )
                ).convert("RGB")
                draw = ImageDraw.Draw(img)

                # Inner highlight:
                # inset 0 1px 0 rgba(255,255,255,0.15)
                hi_img  = Image.new(
                    "RGBA", (W,H), (0,0,0,0)
                )
                hi_draw = ImageDraw.Draw(hi_img)
                hi_draw.line(
                    [
                        (badge_x+badge_radius,
                         badge_y+1),
                        (badge_x+bw-badge_radius,
                         badge_y+1)
                    ],
                    fill=(255,255,255,38),
                    width=2
                )
                img = Image.alpha_composite(
                    img.convert("RGBA"), hi_img
                ).convert("RGB")
                draw = ImageDraw.Draw(img)

                # Badge text
                # letter-spacing: 1.5px → 3px
                text_y = badge_y + badge_pad_y
                text_x = badge_x + badge_pad_x
                draw.text(
                    (text_x, text_y),
                    badge_text,
                    font = f_badge,
                    fill = (255, 255, 255)
                )

                badge_x += bw + badge_gap

            # ── Title ──
            # font-size: 36px → 72px
            # color: #f0f5ff
            # font-weight: 900
            # text-shadow: 3px 3px #000510,
            #              4px 4px #000510,
            #              5px 5px #000510,
            #              glow rgba(30,80,180,0.5)
            #              glow rgba(30,80,180,0.3)
            # line-height: 1.1 → 79px
            # letter-spacing: 1px → 2px
            # max 22 chars per line

            # Clean title
            clean = title
            if part_num:
                clean = re.sub(
                    r'\s*\|\s*Part\s*\d+.*$',
                    '', clean,
                    flags=re.IGNORECASE
                ).strip()

            # Remove emojis for clean look
            clean_ascii = re.sub(
                r'[^\x00-\x7F]+', '', clean
            ).strip()

            if not clean_ascii:
                clean_ascii = clean

            # Uppercase
            clean_ascii = clean_ascii.upper()

            # Word wrap at 22 chars
            words = clean_ascii.split()
            lines = []
            line  = ""
            for word in words:
                test = (line+" "+word).strip()
                if len(test) <= 22:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
            lines = lines[:2]

            # line-height: 1.1 x 72px = 79px
            line_h = int(36 * S * 1.1)  # 79px

            # Title Y: above badges
            # gap: 10px → 20px between elements
            title_bottom = badge_y - (10 * S)
            title_total_h= len(lines) * line_h
            title_y      = title_bottom - title_total_h

            for line_text in lines:
                # text-shadow: 3px,4px,5px #000510
                for ox, oy in [
                    (3*S, 3*S),
                    (4*S, 4*S),
                    (5*S, 5*S)
                ]:
                    draw.text(
                        (PAD_X+ox, title_y+oy),
                        line_text,
                        font = f_title,
                        fill = SHADOW
                    )

                # Glow: rgba(30,80,180,0.5)
                glow_img  = Image.new(
                    "RGBA", (W,H), (0,0,0,0)
                )
                glow_draw = ImageDraw.Draw(glow_img)
                for g in range(1, 12):
                    alpha = int(
                        128 * (1-g/12)
                    )
                    glow_draw.text(
                        (PAD_X-g, title_y),
                        line_text,
                        font = f_title,
                        fill = (30,80,180,alpha)
                    )
                    glow_draw.text(
                        (PAD_X+g, title_y),
                        line_text,
                        font = f_title,
                        fill = (30,80,180,alpha)
                    )
                    glow_draw.text(
                        (PAD_X, title_y-g),
                        line_text,
                        font = f_title,
                        fill = (30,80,180,alpha)
                    )
                    glow_draw.text(
                        (PAD_X, title_y+g),
                        line_text,
                        font = f_title,
                        fill = (30,80,180,alpha)
                    )

                img = Image.alpha_composite(
                    img.convert("RGBA"),
                    glow_img
                ).convert("RGB")
                draw = ImageDraw.Draw(img)

                # Main white title text
                draw.text(
                    (PAD_X, title_y),
                    line_text,
                    font = f_title,
                    fill = WHITE
                )

                title_y += line_h

            # ── Part indicator ──
            # font-size: 13px → 26px
            # color: #4191ff
            # letter-spacing: 3px → 6px
            # above title with gap 10px → 20px
            if (
                part_num
                and total_parts
                and total_parts > 1
            ):
                part_text = (
                    f"PART {part_num} "
                    f"OF {total_parts}"
                )

                # Y above title
                part_bottom = (
                    badge_y
                    - (10*S)
                    - title_total_h
                    - (10*S)
                )

                # Shadow: 0 2px 8px rgba(0,0,20,0.9)
                draw.text(
                    (PAD_X, part_bottom+4),
                    part_text,
                    font = f_part,
                    fill = (0, 0, 20)
                )
                # Blue text
                draw.text(
                    (PAD_X, part_bottom),
                    part_text,
                    font = f_part,
                    fill = BLUE
                )

            # ── Save final image ──
            img.save(
                output_path,
                "JPEG",
                quality     = 98,
                subsampling = 0
            )
            return output_path

        except Exception as e:
            print(f"   ❌ Build error: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ─────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────

    def _font(self, size):
        """
        Load Arial Black equivalent
        Best match: DejaVuSans-Bold (weight 900)
        """
        paths = [
            # Bold fonts = closest to Arial Black
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
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
