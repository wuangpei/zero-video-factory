"""CI smoke test — builds a tiny video end-to-end with NO external API.

Uses a Pillow-generated placeholder image + silent narration WAVs so the
pipeline (labels -> clips -> crossfade -> music -> mix) runs deterministically
without API keys. Real image/TTS backends are validated manually (see README).
"""
import json
import os
import struct
import subprocess
import sys
import wave

import PIL.Image
import PIL.ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import Config
from pipeline import assemble

WORK = ".work-ci"
os.makedirs(WORK, exist_ok=True)


def make_image(path, color, text):
    img = PIL.Image.new("RGB", (1280, 720), color)
    d = PIL.ImageDraw.Draw(img)
    d.text((540, 340), text, fill=(255, 255, 255))
    img.save(path)
    return path


def make_silent_wav(path, seconds=3.0, sr=24000):
    n = int(seconds * sr)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(b"".join(struct.pack("<h", 0) for _ in range(n)))
    return path


def main():
    cfg = Config()  # defaults: 1280x720, fps 25, fade 0.8, calm music
    img1 = make_image(os.path.join(WORK, "a.jpg"), (70, 90, 140), "scene A")
    img2 = make_image(os.path.join(WORK, "b.jpg"), (140, 90, 70), "scene B")
    n1 = make_silent_wav(os.path.join(WORK, "n1.wav"))
    n2 = make_silent_wav(os.path.join(WORK, "n2.wav"))

    master = [
        {"id": 1, "reuse_image": img1, "label": "A", "narration": "test one", "zoom": "in"},
        {"id": 2, "reuse_image": img2, "label": "B", "narration": "test two", "zoom": "out"},
    ]
    os.makedirs(os.path.join(WORK, "narr"), exist_ok=True)
    os.makedirs(os.path.join(WORK, "scenes"), exist_ok=True)
    os.makedirs(os.path.join(WORK, "clips"), exist_ok=True)
    # place narration files where assemble expects them
    for i, p in enumerate([n1, n2], start=1):
        import shutil
        shutil.copy(p, os.path.join(WORK, "narr", f"block{i}.wav"))
    # label the images into scenes/
    from pipeline.labels import add_label
    add_label(cfg, img1, "A", os.path.join(WORK, "scenes", "scene1.jpg"))
    add_label(cfg, img2, "B", os.path.join(WORK, "scenes", "scene2.jpg"))

    out = os.path.join(WORK, "final.mp4")
    out, total = assemble.build(cfg, master,
                                os.path.join(WORK, "narr"),
                                os.path.join(WORK, "scenes"),
                                os.path.join(WORK, "clips"),
                                out)
    assert os.path.exists(out) and os.path.getsize(out) > 50000, "output missing or too small"
    assert total > 10, "video too short"
    print(f"SMOKE OK: {out} ({total:.1f}s, {os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    sys.exit(main())
