"""TTS backends: local VoiceStudio (recommended) or Edge TTS (zero install)."""
import json
import os
import subprocess
import urllib.request
import urllib.error

from .config import Config


def _voicestudio(cfg: Config, text: str, out_path: str) -> str:
    """POST /generate (multipart form) — supports profile_id + fixed seed for a consistent voice."""
    cmd = ["curl", "-s", "--max-time", "600", "-X", "POST", f"{cfg.vs_api}/generate",
           "-F", f"text={text}", "-F", "language=Auto", "-F", f"num_step={cfg.vs_steps}",
           "-F", f"speed={cfg.vs_speed}", "-F", f"seed={cfg.vs_seed}", "-o", out_path]
    if cfg.vs_profile_id:
        cmd += ["-F", f"profile_id={cfg.vs_profile_id}"]
    r = subprocess.run(cmd, capture_output=True)
    if not os.path.exists(out_path) or os.path.getsize(out_path) < 2000:
        raise RuntimeError(f"VoiceStudio TTS failed: {r.stdout[-200:]} {r.stderr[-200:]}")
    return out_path


def _edge(cfg: Config, text: str, out_path: str) -> str:
    try:
        import edge_tts
    except ImportError:
        raise RuntimeError("edge-tts not installed. Run: pip install edge-tts")
    import asyncio

    async def _run():
        tts = edge_tts.Communicate(text, cfg.edge_voice, rate=cfg.edge_rate)
        await tts.save(out_path)

    asyncio.run(_run())
    return out_path


def synthesize(cfg: Config, text: str, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if cfg.tts_backend == "edge":
        return _edge(cfg, text, out_path)
    return _voicestudio(cfg, text, out_path)
