"""Configuration from environment variables (.env or exported)."""
import os
from dataclasses import dataclass, field


def _load_dotenv(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)


@dataclass
class Config:
    image_backend: str = "seedream"          # seedream | openai
    seedream_app_id: str = ""
    seedream_app_key: str = ""
    seedream_endpoint: str = "https://autoglm-api.autoglm.ai/agentdr/v1/assistant/skills/generate-image-seedream"
    seedream_token_url: str = "http://127.0.0.1:18432/get_token"
    openai_base_url: str = ""
    openai_api_key: str = ""
    openai_image_model: str = ""

    tts_backend: str = "voicestudio"         # voicestudio | edge
    vs_api: str = "http://localhost:3900"
    vs_profile_id: str = ""
    vs_seed: str = "42"
    vs_steps: int = 32
    vs_speed: float = 0.9
    edge_voice: str = "vi-VN-HoaiMyNeural"
    edge_rate: str = "-8%"

    font_path: str = ""                      # empty -> auto (Tahoma/arial)
    music_style: str = "calm"                # calm | cheerful
    music_track: str = ""                    # optional external track
    fps: int = 25
    fade: float = 0.8
    width: int = 1280
    height: int = 720
    verify: bool = False

    def __post_init__(self):
        if self.font_path == "":
            for cand in ("C:\\Windows\\Fonts\\Tahoma.ttf",
                         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                         "/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
                if os.path.exists(cand):
                    self.font_path = cand
                    break


def load_config() -> Config:
    _load_dotenv()
    e = os.environ.get
    return Config(
        image_backend=e("IMAGE_BACKEND", "seedream"),
        seedream_app_id=e("SEEDREAM_APP_ID", ""),
        seedream_app_key=e("SEEDREAM_APP_KEY", ""),
        seedream_endpoint=e("SEEDREAM_ENDPOINT", Config.seedream_endpoint),
        seedream_token_url=e("SEEDREAM_TOKEN_URL", Config.seedream_token_url),
        openai_base_url=e("OPENAI_BASE_URL", ""),
        openai_api_key=e("OPENAI_API_KEY", ""),
        openai_image_model=e("OPENAI_IMAGE_MODEL", ""),
        tts_backend=e("TTS_BACKEND", "voicestudio"),
        vs_api=e("VS_API", "http://localhost:3900"),
        vs_profile_id=e("VS_PROFILE_ID", ""),
        vs_seed=e("VS_SEED", "42"),
        vs_steps=int(e("VS_STEPS", "32")),
        vs_speed=float(e("VS_SPEED", "0.9")),
        edge_voice=e("EDGE_VOICE", "vi-VN-HoaiMyNeural"),
        edge_rate=e("EDGE_RATE", "-8%"),
        font_path=e("FONT_PATH", ""),
        music_style=e("MUSIC_STYLE", "calm"),
        music_track=e("MUSIC_TRACK", ""),
        fps=int(e("FPS", "25")),
        fade=float(e("FADE", "0.8")),
        width=int(e("WIDTH", "1280")),
        height=int(e("HEIGHT", "720")),
        verify=e("VERIFY", "0") == "1",
    )
