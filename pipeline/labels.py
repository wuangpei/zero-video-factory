"""Text overlay (bottom banner) via Pillow — Unicode-safe (Thai, Vietnamese, CJK…)."""
from PIL import Image, ImageDraw, ImageFont

from .config import Config


def add_label(cfg: Config, image_path: str, text: str, out_path: str) -> str:
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    target = cfg.width / cfg.height
    ratio = w / h
    if ratio > target:
        nw = int(h * target)
        x0 = (w - nw) // 2
        img = img.crop((x0, 0, x0 + nw, h))
    else:
        nh = int(w / target)
        y0 = (h - nh) // 2
        img = img.crop((0, y0, w, y0 + nh))
    img = img.resize((cfg.width, cfg.height), Image.LANCZOS)

    draw = ImageDraw.Draw(img)
    size = 88 if len(text) <= 6 else 64
    font = ImageFont.truetype(cfg.font_path or "arial.ttf", size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (cfg.width - tw) // 2 - bbox[0]
    y = cfg.height - 160 - bbox[1]
    draw.rectangle([0, cfg.height - 220, cfg.width, cfg.height], fill=(0, 0, 0, 90))
    draw.text((x, y), text, font=font, fill=(255, 226, 140), stroke_width=6, stroke_fill=(40, 20, 0))
    img.save(out_path)
    return out_path
