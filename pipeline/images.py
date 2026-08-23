"""Image generation backends: seedream (AutoGLM), OpenAI-compatible, pollinations, higgsfield."""
import hashlib
import json
import os
import re
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


def _pollinations(cfg: Config, prompt: str, out_path: str) -> str:
    """Free image API, no key needed (pollinations.ai)."""
    import urllib.parse
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
    url += f"?width={cfg.width}&height={cfg.height}&nologo=true"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        with open(out_path, "wb") as f:
            f.write(r.read())
    return out_path


def _higgsfield_generate(cfg: Config, prompt: str, out_path: str) -> str:
    """Nano Banana (Gemini 2.5 Flash Image) via the Higgsfield MCP server.
    Needs the higgsfield connector authorized in the mcporter config."""
    import subprocess as sp
    import time

    node = cfg.higgsfield_node or r"C:\Program Files\AutoClaw\resources\node\node.exe"
    cli = cfg.higgsfield_cli or r"C:\Users\quanlouis\AppData\Roaming\npm\node_modules\mcporter\dist\cli.js"
    mcfg = cfg.higgsfield_mcp_config or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "config", "mcporter.json")
    if not os.path.exists(mcfg):
        raise RuntimeError(f"mcporter config not found: {mcfg}")

    ratio = "16:9" if cfg.width / cfg.height > 1 else "9:16"
    payload = {"params": {"model": cfg.higgsfield_model, "prompt": prompt,
                          "aspect_ratio": ratio, "count": 1}}
    r = sp.run([node, cli, "--config", mcfg, "call", "higgsfield.generate_image",
                "--args", json.dumps(payload)], capture_output=True, text=True,
               encoding="utf-8", errors="replace")
    if "error" in r.stdout.lower() and "job_id" not in r.stdout.lower():
        raise RuntimeError(f"Higgsfield image failed: {r.stdout[:300]}")
    try:
        job_id = json.loads(r.stdout)["results"][0]["id"]
    except Exception:
        raise RuntimeError(f"Higgsfield parse error: {r.stdout[:300]}")

    wpayload = {"jobs": [{"index": 1, "job_id": job_id}], "timeout_seconds": 15}
    url = None
    for _ in range(60):  # up to ~10 min
        r2 = sp.run([node, cli, "--config", mcfg, "call", "higgsfield.jobs_wait",
                     "--args", json.dumps(wpayload)], capture_output=True, text=True,
                    encoding="utf-8", errors="replace")
        out = r2.stdout
        m = re.search(r'"result_url"\s*:\s*"(https://[^"]+)"', out)
        if m:
            url = m.group(1)
            break
        if '"all_terminal": true' in out:
            if '"status": "failed"' in out:
                raise RuntimeError(f"Higgsfield job failed: {out[:300]}")
            break
        time.sleep(10)
    if not url:
        raise RuntimeError("Higgsfield image timeout")
    urllib.request.urlretrieve(url, out_path)
    return out_path


def generate_image(cfg: Config, prompt: str, out_path: str, backend: str = None) -> str:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    backend = backend or cfg.image_backend
    if backend == "openai":
        return _openai_generate(cfg, prompt, out_path)
    if backend == "pollinations":
        return _pollinations(cfg, prompt, out_path)
    if backend == "higgsfield":
        return _higgsfield_generate(cfg, prompt, out_path)
    return _seedream_generate(cfg, prompt, out_path)
