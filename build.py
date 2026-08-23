#!/usr/bin/env python3
"""Zero-Cost Video Factory — build a narrated video from a master.json scene script.

Usage:
  python build.py --config examples/dhamma-thai/master.json [--out out/final.mp4] [--workdir .work]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.config import load_config
from pipeline import images, labels, tts, assemble


def main():
    ap = argparse.ArgumentParser(description="Zero-Cost Video Factory")
    ap.add_argument("--config", required=True, help="master.json scene script")
    ap.add_argument("--out", default="out/final.mp4")
    ap.add_argument("--workdir", default=".work")
    args = ap.parse_args()

    cfg = load_config()
    root = os.path.dirname(os.path.abspath(args.config))
    os.makedirs(args.workdir, exist_ok=True)
    os.makedirs(os.path.join(args.workdir, "scenes"), exist_ok=True)
    os.makedirs(os.path.join(args.workdir, "narr"), exist_ok=True)

    with open(args.config, encoding="utf-8") as f:
        master = json.load(f)

    # 1) images + labels
    for b in master:
        lab = os.path.join(args.workdir, "scenes", f"scene{b['id']}.jpg")
        if os.path.exists(lab) and os.path.getsize(lab) > 50000:
            continue
        if "reuse_image" in b:
            src = b["reuse_image"] if os.path.isabs(b["reuse_image"]) else os.path.join(root, b["reuse_image"])
            os.makedirs(os.path.dirname(lab), exist_ok=True)
            import shutil
            shutil.copy(src, lab)
            if b.get("label"):
                labels.add_label(cfg, lab, b["label"], lab)
            continue
        raw = os.path.join(args.workdir, "scenes", f"raw{b['id']}.jpg")
        images.generate_image(cfg, b["prompt"], raw)
        if b.get("label"):
            labels.add_label(cfg, raw, b["label"], lab)
        else:
            os.replace(raw, lab)
        print("image", b["id"])

    # 2) TTS
    for b in master:
        p = os.path.join(args.workdir, "narr", f"block{b['id']}.wav")
        if os.path.exists(p) and os.path.getsize(p) > 2000:
            continue
        tts.synthesize(cfg, b["narration"], p)
        print("tts", b["id"])

    # 3) assemble
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    out, total = assemble.build(cfg, master,
                                os.path.join(args.workdir, "narr"),
                                os.path.join(args.workdir, "scenes"),
                                args.workdir, args.out)
    print(f"FINAL: {out} ({total:.1f}s)")

    # 4) optional verify
    if cfg.verify:
        try:
            from pipeline import verify
            audio = os.path.join(args.workdir, "audio_full.wav")
            import subprocess as sp
            sp.run(["ffmpeg", "-y", "-v", "error", "-i", args.out, "-vn", "-ac", "1",
                    "-ar", "16000", audio], check=True)
            verify.check(master, os.path.join(args.workdir, "narr"), audio, args.workdir, cfg.fade)
        except ImportError:
            print("VERIFY skipped: faster-whisper not installed")


if __name__ == "__main__":
    sys.exit(main())
