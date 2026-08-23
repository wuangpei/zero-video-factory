"""Assembly: Ken Burns clips + crossfade chain + narration/music mix (ffmpeg)."""
import json
import os
import subprocess
import sys

from .config import Config


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError("CMD FAIL: " + " ".join(cmd)[:250] + "\n" + r.stderr[-1500:])


def _dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def build(cfg: Config, master, narr_dir, scene_dir, workdir, out_path):
    fps, fade = cfg.fps, cfg.fade
    pads = {"intro": 2.0, "scene": 2.2, "outro": 2.5}

    # durations from narration files
    durs = []
    for b in master:
        nd = _dur(os.path.join(narr_dir, f"block{b['id']}.wav"))
        durs.append(max(8.0, nd + pads.get(b.get("kind", "scene"), 2.0)))

    # clips
    for i, b in enumerate(master):
        dst = os.path.join(workdir, f"clip{i+1}.mp4")
        if os.path.exists(dst) and os.path.getsize(dst) > 100000:
            continue
        src = os.path.join(scene_dir, f"scene{b['id']}.jpg")
        frames = int(durs[i] * fps)
        zin = b.get("zoom", "in") == "in"
        zexpr = "min(zoom+0.0009,1.12)" if zin else "max(zoom-0.0009,1.0)"
        vf = (f"scale=2400:-1,zoompan=z='{zexpr}':d={frames}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={cfg.width}x{cfg.height}:fps={fps}")
        _run(["ffmpeg", "-y", "-loop", "1", "-i", src, "-t", f"{durs[i]:.3f}", "-vf", vf,
              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", dst])

    # xfade chain
    inputs = []
    for i in range(len(master)):
        inputs += ["-i", os.path.join(workdir, f"clip{i+1}.mp4")]
    fc, prev = [], "[0:v]"
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    for i in range(1, len(master)):
        off = cum[i] - i * fade
        out = f"[v{i}]"
        fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={fade}:offset={off:.3f}{out}")
        prev = out
    fc.append(f"{prev}format=yuv420p[vout]")
    prev = "[vout]"
    total = cum[-1] - (len(master) - 1) * fade

    # audio: narration at scene offsets + music
    fc2, amix_in, nidx = [], [], len(master)
    for i, b in enumerate(master):
        npath = os.path.join(narr_dir, f"block{b['id']}.wav")
        off_ms = int((cum[i] - ((i - 1) * fade if i > 0 else 0)) * 1000)
        inputs += ["-i", npath]
        fc2.append(f"[{nidx}:a]adelay={off_ms}|{off_ms},apad[a{i}]")
        amix_in.append(f"[a{i}]")
        nidx += 1

    from .music import synth_music
    music = synth_music(cfg, total + 8, os.path.join(workdir, "music.wav"))
    inputs += ["-i", music]
    fc2.append(f"[{nidx}:a]volume=0.13,atrim=0:{total:.2f},afade=t=out:st={total-4:.2f}:d=4[amus]")
    amix_in.append("[amus]")
    fc2.append("".join(amix_in) + f"amix=inputs={len(master)+1}:normalize=0[aout]")

    _run(["ffmpeg", "-y"] + inputs + ["-filter_complex", ";".join(fc + fc2),
          "-map", prev, "-map", "[aout]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
          "-pix_fmt", "yuv420p", "-profile:v", "main",
          "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.2f}", "-movflags", "+faststart", out_path])
    return out_path, total
