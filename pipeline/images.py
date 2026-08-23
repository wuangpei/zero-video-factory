"""Image generation backends: seedream (AutoGLM) or any OpenAI-compatible API."""
import hashlib
import json
import os
import time
import urllib.request
import urllib.error

from .config import Config


def _seedream_generate(cfg: Config, prompt: str, out_path: str) -> str:
    if not cfg.seedream_app_key:
        raise RuntimeError(
            "SEEDREAM_APP_KEY not set. Provide AutoGLM credentials or use IMAGE_BACKEND=openai "
            "with OPENAI_BASE_URL / OPENAI_API_KEY."
        )
    # token (optional local broker; fall back to empty bearer)
    try:
        with urllib.request.urlopen(cfg.seedream_token_url, timeout=5) as r:
            token = r.read().decode().strip()
    except Exception:
        token = ""
    if token and not token.lower().startswith("bearer "):
        token = f"Bearer {token}"
    ts = str(int(time.time()))
    sign = hashlib.md5(f"{cfg.seedream_app_id}&{ts}&{cfg.seedream_app_key}".encode()).hexdigest()
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "X-Auth-Appid": cfg.seedream_app_id,
        "X-Auth-TimeStamp": ts,
        "X-Auth-Sign": sign,
    }
    req = urllib.request.Request(cfg.seedream_endpoint,
                                 data=json.dumps({"query": prompt}).encode(),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read().decode())
    url = data["data"]["image_url"]
    urllib.request.urlretrieve(url, out_path)
    return out_path


def _openai_generate(cfg: Config, prompt: str, out_path: str) -> str:
    if not cfg.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set (IMAGE_BACKEND=openai).")
    base = (cfg.openai_base_url or "https://api.openai.com/v1").rstrip("/")
    model = cfg.openai_image_model or "gpt-image-1"
    headers = {"Authorization": f"Bearer {cfg.openai_api_key}", "Content-Type": "application/json"}
    body = {"model": model, "prompt": prompt, "n": 1}
    req = urllib.request.Request(f"{base}/images/generations",
                                 data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read().decode())
    item = data["data"][0]
    if "url" in item and item["url"]:
        urllib.request.urlretrieve(item["url"], out_path)
    elif "b64_json" in item and item["b64_json"]:
        import base64
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(item["b64_json"]))
    else:
        raise RuntimeError(f"No image in response: {str(data)[:300]}")
    return out_path


def generate_image(cfg: Config, prompt: str, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if cfg.image_backend == "openai":
        return _openai_generate(cfg, prompt, out_path)
    return _seedream_generate(cfg, prompt, out_path)
