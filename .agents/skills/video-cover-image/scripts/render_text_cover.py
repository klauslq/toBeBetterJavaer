#!/usr/bin/env python3
import argparse
import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


WHITE = (253, 253, 249, 255)
YELLOW = (255, 238, 48, 255)
DARK = (22, 26, 26, 255)
SHADOW = (0, 0, 0, 155)


def resolve_font():
    candidates = [
        "Hiragino Sans GB:style=W6",
        "PingFang SC:style=Semibold",
        "Arial Unicode MS",
    ]
    for candidate in candidates:
        try:
            path = subprocess.check_output(
                ["fc-match", "-f", "%{file}\n", candidate], text=True
            ).strip()
            index = int(
                subprocess.check_output(
                    ["fc-match", "-f", "%{index}\n", candidate], text=True
                ).strip()
                or 0
            )
        except Exception:
            continue
        if path:
            return path, index
    raise SystemExit("No usable CJK font found")


FONT_FILE, FONT_INDEX = resolve_font()


def make_font(size):
    return ImageFont.truetype(FONT_FILE, size, index=FONT_INDEX)


def text_bbox(text, font):
    draw = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    return draw.textbbox((0, 0), text, font=font)


def fit_font(text, max_width, start_size, min_size):
    for size in range(start_size, min_size - 1, -2):
        font = make_font(size)
        box = text_bbox(text, font)
        if box[2] - box[0] <= max_width:
            return font
    return make_font(min_size)


def charcoal_background(width, height, seed):
    random.seed(seed)
    base = Image.new("RGBA", (width, height), DARK)

    noise = Image.effect_noise((width, height), 35).convert("L")
    noise = ImageEnhance.Contrast(noise).enhance(0.85)
    noise = noise.filter(ImageFilter.GaussianBlur(0.45))
    alpha = Image.new("L", (width, height), 18)
    base = Image.alpha_composite(base, Image.merge("RGBA", (noise, noise, noise, alpha)))

    scratches = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scratches)
    for _ in range(46):
        x = random.randint(-width // 10, width)
        y = random.randint(-height // 10, height)
        length = random.randint(width // 8, width // 4)
        angle = random.uniform(-0.42, 0.42)
        shade = random.randint(40, 64)
        alpha_value = random.randint(7, 16)
        draw.line(
            [
                (x, y),
                (
                    x + int(length * math.cos(angle)),
                    y + int(length * math.sin(angle)),
                ),
            ],
            fill=(shade, shade, shade, alpha_value),
            width=1,
        )
    base = Image.alpha_composite(base, scratches.filter(ImageFilter.GaussianBlur(1.2)))

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse(
        [
            int(width * 0.08),
            int(height * 0.04),
            int(width * 0.92),
            int(height * 0.86),
        ],
        fill=(58, 62, 58, 58),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(int(min(width, height) * 0.13)))
    return Image.alpha_composite(base, glow)


def draw_centered(image, y, text, font, color, shadow_dx=5, shadow_dy=6):
    draw = ImageDraw.Draw(image)
    x = image.width // 2
    draw.text((x + shadow_dx, y + shadow_dy), text, font=font, fill=SHADOW, anchor="mt")
    draw.text((x, y), text, font=font, fill=color, anchor="mt")


def render(width, height, title, lines, vertical):
    image = charcoal_background(width, height, 202 if vertical else 101)
    title_font = fit_font(
        title,
        int(width * (0.88 if vertical else 0.86)),
        int(height * (0.094 if vertical else 0.137)),
        int(height * (0.067 if vertical else 0.100)),
    )
    title_y = int(height * (0.339 if vertical else 0.292))
    draw_centered(image, title_y, title, title_font, WHITE)

    if not lines:
        return image.convert("RGB")

    max_width = int(width * (0.88 if vertical else 0.84))
    start_size = int(height * (0.056 if vertical else 0.081))
    min_size = int(height * (0.039 if vertical else 0.057))
    fonts = [fit_font(line, max_width, start_size, min_size) for line in lines]

    if len(lines) == 1:
        ys = [int(height * (0.55 if vertical else 0.54))]
    else:
        top = height * (0.52 if vertical else 0.52)
        gap = height * (0.079 if vertical else 0.104)
        ys = [int(top + index * gap) for index in range(len(lines))]

    for y, line, font in zip(ys, lines, fonts):
        draw_centered(image, y, line, font, YELLOW, 4, 5)

    return image.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description="Render black/gray pure-text video covers.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--line", action="append", default=[])
    parser.add_argument("--prefix", default="video-cover")
    parser.add_argument("--out-dir", default=str(Path.home() / "Downloads"))
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    horizontal = render(1440, 1080, args.title, args.line, vertical=False)
    vertical = render(1080, 1440, args.title, args.line, vertical=True)

    horizontal_path = out_dir / f"{args.prefix}-horizontal-4x3.png"
    vertical_path = out_dir / f"{args.prefix}-vertical-3x4.png"
    horizontal.save(horizontal_path, quality=94)
    vertical.save(vertical_path, quality=94)
    print(horizontal_path)
    print(vertical_path)


if __name__ == "__main__":
    main()
