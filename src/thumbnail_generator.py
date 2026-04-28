"""
Thumbnail Generator
Creates YouTube thumbnails for rain sleep videos
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont


THUMB_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "thumbnails"
)

os.makedirs(THUMB_DIR, exist_ok=True)

# Rain sleep color schemes
COLOR_SCHEMES = [
    {
        "bg"      : (10,  20,  40),
        "accent"  : (50,  100, 200),
        "text"    : (200, 220, 255),
        "subtext" : (150, 180, 220),
    },
    {
        "bg"      : (5,   15,  30),
        "accent"  : (30,  80,  160),
        "text"    : (180, 210, 255),
        "subtext" : (130, 170, 220),
    },
    {
        "bg"      : (15,  25,  50),
        "accent"  : (60,  120, 220),
        "text"    : (220, 235, 255),
        "subtext" : (160, 190, 230),
    },
]


class ThumbnailGenerator:

    def generate(
        self,
        title,
        part_num=None,
        total_parts=None,
        duration_str=""
    ):
        """Generate thumbnail and return file path"""

        output_id   = f"thumb_{part_num or 1}"
        output_path = os.path.join(
            THUMB_DIR, f"{output_id}.jpg"
        )

        scheme = random.choice(COLOR_SCHEMES)

        # Create image 1280x720
        img  = Image.new("RGB", (1280, 720), scheme["bg"])
        draw = ImageDraw.Draw(img)

        # Draw rain effect (vertical lines)
        import random as rnd
        for _ in range(200):
            x  = rnd.randint(0, 1280)
            y  = rnd.randint(0, 720)
            y2 = y + rnd.randint(10, 40)
            opacity = rnd.randint(30, 100)
            draw.line(
                [(x, y), (x + 2, y2)],
                fill=(
                    scheme["accent"][0],
                    scheme["accent"][1],
                    scheme["accent"][2],
                ),
                width=1
            )

        # Draw gradient overlay at bottom
        for i in range(200):
            alpha = int(i * 1.2)
            draw.rectangle(
                [(0, 520 + i), (1280, 521 + i)],
                fill=(
                    scheme["bg"][0],
                    scheme["bg"][1],
                    scheme["bg"][2],
                )
            )

        # Try to load font
        try:
            font_large = ImageFont.truetype(
                "/usr/share/fonts/truetype/"
                "dejavu/DejaVuSans-Bold.ttf",
                72
            )
            font_medium = ImageFont.truetype(
                "/usr/share/fonts/truetype/"
                "dejavu/DejaVuSans.ttf",
                40
            )
            font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/"
                "dejavu/DejaVuSans.ttf",
                32
            )
        except Exception:
            font_large  = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small  = ImageFont.load_default()

        # Draw rain emoji / icon area
        draw.ellipse(
            [(540, 80), (740, 280)],
            fill=scheme["accent"]
        )

        # Draw rain drops in circle
        for i in range(8):
            x  = 580 + (i % 4) * 40
            y  = 120 + (i // 4) * 80
            draw.ellipse(
                [(x, y), (x+8, y+20)],
                fill=scheme["text"]
            )

        # Draw title text
        # Wrap title if too long
        words     = title.split()
        lines     = []
        line      = ""
        for word in words:
            if len(line + word) < 28:
                line += word + " "
            else:
                if line:
                    lines.append(line.strip())
                line = word + " "
        if line:
            lines.append(line.strip())

        # Draw each line
        y_start = 320
        for line in lines[:3]:
            draw.text(
                (640, y_start),
                line,
                font=font_large,
                fill=scheme["text"],
                anchor="mm"
            )
            y_start += 80

        # Draw duration
        if duration_str:
            draw.text(
                (640, 580),
                f"⏱ {duration_str}",
                font=font_medium,
                fill=scheme["subtext"],
                anchor="mm"
            )

        # Draw part number
        if part_num and total_parts and total_parts > 1:
            draw.text(
                (640, 630),
                f"Part {part_num} of {total_parts}",
                font=font_small,
                fill=scheme["subtext"],
                anchor="mm"
            )

        # Draw channel watermark
        draw.text(
            (640, 680),
            "🌧️ Heavy Rain Deep Sleep",
            font=font_small,
            fill=scheme["subtext"],
            anchor="mm"
        )

        # Save
        img.save(output_path, "JPEG", quality=95)
        print(f"   ✅ Thumbnail: {output_path}")
        return output_path