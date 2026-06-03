import math
import os

from PIL import Image, ImageDraw, ImageFont

from .config import FrameConfig

_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf",
    "/usr/share/fonts/opentype/urw-base35/URWGothic-Book.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:\\Windows\\Fonts\\arialbd.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
]


def _find_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _create_gradient(
    width: int, height: int, c1: str, c2: str, direction: str
) -> Image.Image:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    canvas = Image.new("RGB", (width, height))
    pixels = canvas.load()

    if direction == "horizontal":
        for x in range(width):
            t = x / max(width - 1, 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            for y in range(height):
                pixels[x, y] = (r, g, b)

    elif direction == "vertical":
        for y in range(height):
            t = y / max(height - 1, 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            for x in range(width):
                pixels[x, y] = (r, g, b)

    elif direction == "diagonal":
        max_dist = width + height
        for y in range(height):
            for x in range(width):
                t = (x + y) / max(max_dist - 1, 1)
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                pixels[x, y] = (r, g, b)

    elif direction == "anti-diagonal":
        max_dist = width + height
        for y in range(height):
            for x in range(width):
                t = (width - x + y) / max(max_dist - 1, 1)
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                pixels[x, y] = (r, g, b)

    elif direction == "radial":
        cx, cy = width / 2, height / 2
        max_radius = math.sqrt(cx * cx + cy * cy)
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                t = dist / max(max_radius, 1)
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                pixels[x, y] = (r, g, b)

    else:
        canvas.paste((r1, g1, b1), (0, 0, width, height))

    return canvas


def add_frame_and_caption(
    image_path: str,
    output_path: str,
    frame_config: FrameConfig,
    caption: str,
) -> Image.Image:
    source = Image.open(image_path)
    if source.mode not in ("RGB", "RGBA"):
        source = source.convert("RGB")

    t = frame_config.thickness
    src_w, src_h = source.size
    total_w = src_w + 2 * t
    total_h = src_h + 2 * t

    if frame_config.gradient_enabled:
        canvas = _create_gradient(
            total_w, total_h,
            frame_config.color,
            frame_config.gradient_color2,
            frame_config.gradient_direction,
        )
    else:
        bg_color = _hex_to_rgb(frame_config.color)
        canvas = Image.new("RGB", (total_w, total_h), bg_color)

    canvas.paste(source, (t, t))

    draw = ImageDraw.Draw(canvas)

    headline = frame_config.headline.strip()
    if headline:
        font = _find_font(frame_config.font_size)
        _draw_text_in_band(draw, headline, font, total_w, 0, t, "white")

    if caption.strip():
        caption_font_size = max(16, frame_config.font_size - 4)
        caption_font = _find_font(caption_font_size)
        _draw_text_in_band(
            draw, caption, caption_font, total_w, total_h - t, total_h, "white"
        )

    canvas.save(output_path, format="PNG")
    return canvas


def _draw_text_in_band(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    band_width: int,
    band_top: int,
    band_bottom: int,
    fill: str,
) -> None:
    band_height = band_bottom - band_top
    padding = 8
    usable_width = band_width - 40
    lines = _wrap_text(text, font, usable_width)
    line_height = font.size + 4
    total_text_height = len(lines) * line_height

    y = band_top + (band_height - total_text_height) // 2 + padding
    y = max(band_top + padding, y)

    for line in lines:
        bbox = font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        x = (band_width - line_width) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        line_w = bbox[2] - bbox[0]
        if line_w <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines if lines else [text]
