"""Background music synthesis — pure Python stdlib, no assets.

calm: slow pentatonic pad + soft bell (Dhamma/bedtime)
cheerful: bright arpeggio music-box (kids content)
"""
import math
import struct
import wave

from .config import Config


def synth_music(cfg: Config, duration_sec: float, out_path: str) -> str:
    if cfg.music_track:
        return cfg.music_track  # user-provided track wins

    SR = 44100
    n = int(duration_sec * SR)
    samples = [0.0] * n

    if cfg.music_style == "cheerful":
        melody = [523.25, 659.25, 783.99, 1046.50, 783.99, 659.25, 587.33, 659.25]
        bass = [261.63, 261.63, 293.66, 261.63]
        note_len, gap, amp, bamp = 1.1, 0.45, 0.20, 0.14
    else:  # calm
        melody = [196.0, 220.0, 261.63, 293.66, 329.63]
        bass = []
        note_len, gap, amp, bamp = 3.6, 3.6, 0.11, 0.0

    def add_note(freq, start, length, a):
        for k in range(int(length * SR)):
            tt = k / SR
            env = math.exp(-3.2 * tt / length)
            v = math.sin(2 * math.pi * freq * tt) + 0.3 * math.sin(2 * math.pi * freq * 2 * tt) * math.exp(-6 * tt / length)
            pos = int((start + tt) * SR)
            if pos < n:
                samples[pos] += a * env * v

    t, idx = 0.0, 0
    while t < duration_sec - note_len - 1:
        add_note(melody[idx % len(melody)], t, note_len, amp)
        if bass:
            add_note(bass[(idx // 4) % len(bass)], t, note_len * 1.4, bamp)
        if cfg.music_style == "calm" and idx % 4 == 0:  # soft bell
            for k in range(int(2.0 * SR)):
                tt = k / SR
                bell = math.exp(-2.0 * tt / 2.0) * math.sin(2 * math.pi * 880 * tt)
                pos = int((t + tt) * SR)
                if pos < n:
                    samples[pos] += 0.05 * bell
        t += gap
        idx += 1

    peak = max(abs(x) for x in samples) or 1.0
    with wave.open(out_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(b"".join(
            struct.pack("<h", int(max(-1, min(1, x / peak)) * 0.45 * 32767)) for x in samples
        ))
    return out_path
