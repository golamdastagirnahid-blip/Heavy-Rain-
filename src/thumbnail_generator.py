"""
Thumbnail Generator
100% pixel accurate match to HTML preview
Takes real screenshot from stock footage
"""

import os
import re
import json
import math
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

# Exact colors from HTML
BG_1         = (10,  22,  40)
BG_2         = (13,  32,  64)
BG_3         = (10,  24,  48)
BG_4         = (6,   14,  30)
BLUE         = (65,  145, 255)
WHITE        = (240, 245, 255)
SHADOW       = (0,   5,   16)
BADGE_DUR    = (37,  99,  235)
BADGE_DUR2   = (29,  78,  216)
BADGE_ADS    = (22,  163,  74)
BADGE_ADS2   = (21,  128,  61)
BADGE_SLP    = (124,  58, 237)
BADGE_SLP2   = (109,  40, 217)
BADGE_HD     = (220,  38,  38)
BADGE_HD2    = (185,  28,  28)


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

        # Get background from footage
        bg = None
        if footage_path and os.path.exists(
            footage_path
        ):
            bg = self._extract_frame(
                footage_path, frame_path
            )

        if not bg:
            bg = self._make_bg(frame_path)

        result = self._build(
            bg_path      = bg,
            output_path  = output_path,
            title        = title,
            part_num     = part_num,
            total_parts  = total_parts,
            duration_str = duration_str
        )

        if result:
            print(
                f"   ✅ Thumbnail: "
                f"{os.path.getsize(result)//1024}KB"
            )
            return result

        return None

    def _extract_frame(
        self, footage_path, frame_path
    ):
        """
        Extract real screenshot from footage
        Random timestamp between 20%-80%
        """
        if not footage_path:
            return None
        if not os.path.exists(footage_path):
            print(
                f"   ⚠️ Footage missing: "
                f"{footage_path}"
            )
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

            # Random frame 20%-80%
            ts = random.uniform(
                dur * 0.2, dur * 0.8
            )

            print(
                f"   📸 Screenshot at {ts:.1f}s"
            )

            cmd = [
                "ffmpeg", "-y",
                "-ss", str(ts),
                "-i", footage_path,
                "-vframes", "1",
                "-vf", (
                    "scale=1280:720:"
                    "force_original_aspect_ratio"
                    "=increase,crop=1280:720"
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
                    f"   ✅ Frame extracted: "
                    f"{os.path.getsize(frame_path)//1024}KB"
                )
                return frame_path

            print(
                f"   ⚠️ FFmpeg frame failed: "
                f"{r.stderr[-100:]}"
            )
            return None

        except Exception as e:
            print(f"   ⚠️ Frame error: {e}")
            return None

    def _make_bg(self, output_path):
        """
        Rain background matching HTML CSS
        gradient 135deg #0a1628→#0d2040→#0a1830→#060e1e
        """
        try:
            W, H = 1280, 720
            img  = Image.new("RGB", (W, H))
            draw = ImageDraw.Draw(img)

            for y in range(H):
                for x in range(0, W, 4):
                    t = (x/W + y/H) / 2
                    if t < 0.30:
                        p = t / 0.30
                        c = self._lerp(BG_1,BG_2,p)
                    elif t < 0.60:
                        p = (t-0.30) / 0.30
                        c = self._lerp(BG_2,BG_3,p)
                    else:
                        p = (t-0.60) / 0.40
                        c = self._lerp(BG_3,BG_4,p)
                    draw.rectangle(
                        [(x,y),(x+3,y)], fill=c
                    )

            # Rain streaks
            for _ in range(500):
                x   = random.randint(0, W)
                y   = random.randint(-50, H)
                h   = random.randint(30, 110)
                opa = random.uniform(0.2, 0.7)
                col = (
                    int(100*opa),
                    int(160*opa),
                    int(255*opa)
                )
                draw.line(
                    [(x,y),(x+1,y+h)],
                    fill=col, width=1
                )

            img.save(output_path,"JPEG",quality=98)
            return output_path

        except Exception as e:
            print(f"   ⚠️ BG error: {e}")
            img = Image.new("RGB",(1280,720),BG_1)
            img.save(output_path,"JPEG",quality=98)
            return output_path

    def _lerp(self, c1, c2, t):
        return (
            int(c1[0]*(1-t)+c2[0]*t),
            int(c1[1]*(1-t)+c2[1]*t),
            int(c1[2]*(1-t)+c2[2]*t),
        )

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
        Build thumbnail exactly like HTML
        Scale factor S=2 (640x360 → 1280x720)
        """
        try:
            W, H, S = 1280, 720, 2

            # Padding from HTML: 20px 28px x2
            PAD_X = 28 * S   # 56
            PAD_Y = 20 * S   # 40

            # Open bg
            img = Image.open(
                bg_path
            ).convert("RGBA")
            img = img.resize(
                (W, H), Image.LANCZOS
            )

            # Color grade
            img_rgb = img.convert("RGB")
            img_rgb = ImageEnhance.Brightness(
                img_rgb
            ).enhance(0.78)
            img_rgb = ImageEnhance.Contrast(
                img_rgb
            ).enhance(1.2)
            img = img_rgb.convert("RGBA")

            draw = ImageDraw.Draw(img)

            # ── Bottom gradient 75% ──
            bot_start = H - int(H * 0.75)
            bot_h     = int(H * 0.75)
            for i in range(bot_h):
                t = i / bot_h
                if t < 0.30:
                    p = t / 0.30
                    a = int(p * 128)
                    c = (5, 12, 30, a)
                elif t < 0.60:
                    p = (t-0.30) / 0.30
                    a = int(128 + p*89)
                    c = (5, 12, 30, a)
                else:
                    p = (t-0.60) / 0.40
                    a = int(217 + p*30)
                    r = int(5-p*2)
                    g = int(12-p*4)
                    b = int(30-p*10)
                    c = (r, g, b, a)
                draw.rectangle(
                    [
                        (0, bot_start+i),
                        (W, bot_start+i+1)
                    ],
                    fill=c
                )

            # ── Top gradient 35% ──
            top_h = int(H * 0.35)
            for i in range(top_h):
                t = 1 - (i / top_h)
                a = int(t * 128)
                draw.rectangle(
                    [(0,i),(W,i+1)],
                    fill=(5,12,30,a)
                )

            # ── Left vignette 30% ──
            vig_w = int(W * 0.30)
            for i in range(vig_w):
                t = 1 - (i/vig_w)
                a = int(t * 179)
                draw.rectangle(
                    [(i,0),(i+1,H)],
                    fill=(0,0,15,a)
                )

            # ── Right vignette 30% ──
            for i in range(vig_w):
                t = 1 - (i/vig_w)
                a = int(t * 179)
                draw.rectangle(
                    [(W-1-i,0),(W-i,H)],
                    fill=(0,0,15,a)
                )

            img  = img.convert("RGB")
            draw = ImageDraw.Draw(img)

            # ── Fonts ──
            # HTML sizes x2
            f_chan  = self._font(11*S)  # 22px
            f_part  = self._font(13*S)  # 26px
            f_title = self._font(36*S)  # 72px
            f_badge = self._font(11*S)  # 22px
            f_icon  = self._font(26*S)  # 52px

            # ── Brand bar ──
            # 3px x 26px → 6px x 52px
            bar_x = PAD_X
            bar_w = 3 * S
            bar_h = 26 * S
            top_y = PAD_Y

            draw.rectangle(
                [
                    (bar_x,       top_y),
                    (bar_x+bar_w, top_y+bar_h)
                ],
                fill=BLUE
            )

            # ── Channel name ──
            chan_x = bar_x + bar_w + (8*S)
            chan_y = top_y + 2

            # Shadow
            draw.text(
                (chan_x, chan_y+4),
                "HEAVY RAIN DEEP SLEEP",
                font=f_chan,
                fill=(0,0,0)
            )
            # Blue text
            draw.text(
                (chan_x, chan_y),
                "HEAVY RAIN DEEP SLEEP",
                font=f_chan,
                fill=BLUE
            )

            # ── Rain icon top right ──
            try:
                bbox  = draw.textbbox(
                    (0,0),"🌧️",font=f_icon
                )
                iw    = bbox[2]-bbox[0]
                icon_x= W - PAD_X - iw
                draw.text(
                    (icon_x, top_y),
                    "🌧️",
                    font=f_icon,
                    fill=WHITE
                )
            except Exception:
                pass

            # ── Badges ──
            bpx = 12*S   # pad x
            bpy = 5*S    # pad y
            bgap= 8*S    # gap
            brad= 6*S    # radius

            # Measure badge height
            bb   = draw.textbbox(
                (0,0),"TEST",font=f_badge
            )
            bth  = bb[3]-bb[1]
            bh   = bth + bpy*2

            badge_y = H - PAD_Y - bh
            badge_x = PAD_X

            badges = [
                (
                    f"⏱ {duration_str.upper()}",
                    BADGE_DUR, BADGE_DUR2
                ),
                ("✓ NO ADS",    BADGE_ADS, BADGE_ADS2),
                ("😴 SLEEP AID",BADGE_SLP, BADGE_SLP2),
                ("HD",          BADGE_HD,  BADGE_HD2),
            ]

            for btext, c1, c2 in badges:
                try:
                    tb = draw.textbbox(
                        (0,0),btext,font=f_badge
                    )
                    tw = tb[2]-tb[0]
                except Exception:
                    tw = len(btext)*13

                bw = tw + bpx*2

                # Shadow
                simg = Image.new(
                    "RGBA",(W,H),(0,0,0,0)
                )
                sd   = ImageDraw.Draw(simg)
                for s in range(1,5):
                    al = int(128*(1-s/5))
                    sd.rounded_rectangle(
                        [
                            (badge_x+s,badge_y+s),
                            (badge_x+bw+s,
                             badge_y+bh+s)
                        ],
                        radius=brad,
                        fill=(0,0,0,al)
                    )
                img = Image.alpha_composite(
                    img.convert("RGBA"), simg
                ).convert("RGB")
                draw = ImageDraw.Draw(img)

                # Gradient badge
                bi   = Image.new(
                    "RGBA",(W,H),(0,0,0,0)
                )
                bd   = ImageDraw.Draw(bi)
                for gi in range(bh):
                    t  = gi/bh
                    gr = int(c1[0]*(1-t)+c2[0]*t)
                    gg = int(c1[1]*(1-t)+c2[1]*t)
                    gb = int(c1[2]*(1-t)+c2[2]*t)
                    bd.rectangle(
                        [
                            (badge_x,badge_y+gi),
                            (badge_x+bw,badge_y+gi+1)
                        ],
                        fill=(gr,gg,gb,255)
                    )

                # Clip to rounded rect
                mask = Image.new("L",(W,H),0)
                md   = ImageDraw.Draw(mask)
                md.rounded_rectangle(
                    [
                        (badge_x,badge_y),
                        (badge_x+bw,badge_y+bh)
                    ],
                    radius=brad, fill=255
                )
                img = Image.alpha_composite(
                    img.convert("RGBA"),
                    Image.composite(
                        bi,
                        Image.new(
                            "RGBA",(W,H),(0,0,0,0)
                        ),
                        mask
                    )
                ).convert("RGB")
                draw = ImageDraw.Draw(img)

                # Badge text
                draw.text(
                    (badge_x+bpx, badge_y+bpy),
                    btext,
                    font=f_badge,
                    fill=(255,255,255)
                )

                badge_x += bw + bgap

            # ── Title ──
            # Clean and uppercase
            clean = title
            if part_num:
                clean = re.sub(
                    r'\s*\|\s*Part\s*\d+.*$',
                    '', clean,
                    flags=re.IGNORECASE
                ).strip()

            clean = re.sub(
                r'[^\x00-\x7F]+','',clean
            ).strip().upper()

            if not clean:
                clean = re.sub(
                    r'[^\x00-\x7F]+','',title
                ).strip().upper()

            # Word wrap 22 chars
            words = clean.split()
            lines = []
            line  = ""
            for w in words:
                test = (line+" "+w).strip()
                if len(test) <= 22:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = w
            if line:
                lines.append(line)
            lines = lines[:2]

            # line-height 1.1 x 72px = 79px
            lh = int(36*S*1.1)

            title_total = len(lines) * lh
            title_y     = (
                badge_y - (10*S) - title_total
            )

            for ln in lines:
                # Shadows: 3px,4px,5px #000510
                for ox,oy in [
                    (3*S,3*S),(4*S,4*S),(5*S,5*S)
                ]:
                    draw.text(
                        (PAD_X+ox, title_y+oy),
                        ln,
                        font=f_title,
                        fill=SHADOW
                    )

                # Glow rgba(30,80,180)
                gi  = Image.new(
                    "RGBA",(W,H),(0,0,0,0)
                )
                gd  = ImageDraw.Draw(gi)
                for g in range(1,10):
                    al = int(128*(1-g/10))
                    for ox,oy in [
                        (-g,0),(g,0),(0,-g),(0,g)
                    ]:
                        gd.text(
                            (PAD_X+ox,title_y+oy),
                            ln,
                            font=f_title,
                            fill=(30,80,180,al)
                        )
                img = Image.alpha_composite(
                    img.convert("RGBA"),gi
                ).convert("RGB")
                draw = ImageDraw.Draw(img)

                # White main text
                draw.text(
                    (PAD_X, title_y),
                    ln,
                    font=f_title,
                    fill=WHITE
                )
                title_y += lh

            # ── Part indicator ──
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
                    badge_y
                    - (10*S)
                    - title_total
                    - (10*S)
                    - (13*S*2)
                )
                # Shadow
                draw.text(
                    (PAD_X, py+4),
                    pt,
                    font=f_part,
                    fill=(0,0,20)
                )
                # Blue
                draw.text(
                    (PAD_X, py),
                    pt,
                    font=f_part,
                    fill=BLUE
                )

            # Save
            img.save(
                output_path,"JPEG",
                quality=98,subsampling=0
            )
            return output_path

        except Exception as e:
            print(f"   ❌ Build error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _font(self, size):
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
