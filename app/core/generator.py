"""
Placeholder image generator using Pillow.
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass, field
from typing import Literal

from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------

@dataclass
class PlaceholderConfig:
    width: int = 800
    height: int = 600
    bg_color: str = "#cccccc"
    # gradient
    gradient: bool = False
    gradient_colors: list[str] = field(default_factory=lambda: ["#4facfe", "#00f2fe"])
    gradient_angle: int = 135  # degrees
    # text
    text: str = ""
    text_color: str = "#333333"
    font_size: int = 0          # 0 = auto
    text_align: Literal["center"] = "center"
    # output
    fmt: Literal["PNG", "JPEG", "WEBP"] = "PNG"
    quality: int = 90           # JPEG / WEBP


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6 or not all(c in "0123456789abcdefABCDEF" for c in h):
        raise ValueError(f"Invalid HEX color: '{hex_color}'")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return r, g, b


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_color(
    c1: tuple[int, int, int], c2: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    return (
        int(_lerp(c1[0], c2[0], t)),
        int(_lerp(c1[1], c2[1], t)),
        int(_lerp(c1[2], c2[2], t)),
    )


def _multi_lerp(
    colors: list[tuple[int, int, int]], t: float
) -> tuple[int, int, int]:
    """Interpolate across multiple color stops."""
    n = len(colors) - 1
    if t >= 1.0:
        return colors[-1]
    segment = t * n
    idx = int(segment)
    local_t = segment - idx
    return _lerp_color(colors[idx], colors[idx + 1], local_t)


def _build_gradient(
    width: int,
    height: int,
    hex_colors: list[str],
    angle_deg: int,
) -> Image.Image:
    """Create a linear-gradient PIL Image."""
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    colors = [_hex_to_rgb(c) for c in hex_colors]
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    cx, cy = width / 2, height / 2
    max_proj = abs(cos_a * cx) + abs(sin_a * cy)
    if max_proj == 0:
        max_proj = 1

    for y in range(height):
        for x in range(width):
            proj = cos_a * (x - cx) + sin_a * (y - cy)
            t = (proj + max_proj) / (2 * max_proj)
            t = max(0.0, min(1.0, t))
            pixels[x, y] = _multi_lerp(colors, t)

    return img


def _auto_font_size(width: int, height: int, text: str) -> int:
    """Choose a font size that roughly fits the text inside the image."""
    base = min(width, height) // 8
    # scale down if text is long
    chars = max(len(text), 1)
    scale = max(1, chars // 10)
    return max(12, base // scale)


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a nice font, fall back to default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_placeholder(cfg: PlaceholderConfig) -> io.BytesIO:
    """
    Generate a placeholder image from *cfg* and return it as a BytesIO buffer.
    """
    width = max(1, min(cfg.width, 5000))
    height = max(1, min(cfg.height, 5000))

    # --- background --------------------------------------------------------
    if cfg.gradient and len(cfg.gradient_colors) >= 2:
        img = _build_gradient(width, height, cfg.gradient_colors, cfg.gradient_angle)
    else:
        img = Image.new("RGB", (width, height), _hex_to_rgb(cfg.bg_color))

    # --- text --------------------------------------------------------------
    text = cfg.text or f"{width}×{height}"
    font_size = cfg.font_size if cfg.font_size > 0 else _auto_font_size(width, height, text)
    font = _get_font(font_size)

    draw = ImageDraw.Draw(img)

    # measure text
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = (width - tw) / 2 - bbox[0]
    y = (height - th) / 2 - bbox[1]

    # subtle shadow for readability
    shadow_offset = max(1, font_size // 20)
    shadow_color = (0, 0, 0, 80)
    shadow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, shadow_img)
    img = img.convert("RGB")

    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, font=font, fill=_hex_to_rgb(cfg.text_color))

    # --- encode ------------------------------------------------------------
    buf = io.BytesIO()
    fmt = cfg.fmt.upper()
    if fmt == "JPEG":
        img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=cfg.quality, optimize=True)
    elif fmt == "WEBP":
        img.save(buf, format="WEBP", quality=cfg.quality)
    else:
        img.save(buf, format="PNG", optimize=True)

    buf.seek(0)
    return buf
