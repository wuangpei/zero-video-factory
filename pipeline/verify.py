"""Optional sync check: transcribe the final audio (faster-whisper) and compare
each scene's narration against its time window. Catches wrong audio placement
and hallucinated takes."""
import json
import os
import re
import subprocess
import unicodedata


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return set(re.sub(r"[^a-z0-9]+", " ", s).split())


def _dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def check(master, narr_dir, audio_path, workdir, fade=0.8):
    from faster_whisper import WhisperModel  # optional dependency

    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(audio_path, language=None, word_timestamps=True, vad_filter=True)
    words = [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in (s.words or [])]

    durs = [_dur(os.path.join(narr_dir, f"block{b['id']}.wav")) for b in master]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)

    bad = []
    for i, b in enumerate(master):
        start = cum[i] - ((i - 1) * fade if i > 0 else 0)
        end = start + durs[i]
        exp = _norm(b["narration"])
        win = [w for w in words if start <= w["s"] < end]
        got = _norm(" ".join(w["w"] for w in win))
        pct = 100.0 * sum(1 for w in exp if w in got) / max(1, len(exp))
        ok = pct >= 60
        print(f"scene {b['id']:>2}: {pct:5.0f}% {'OK' if ok else 'MISMATCH'}")
        if not ok:
            bad.append(b["id"])
    print("VERIFY:", "ALL OK" if not bad else f"check scenes {bad}")
    return bad
