# Zero-Cost Video Factory

Turn a topic into a finished narrated video — images, voice-over, background music, captions and assembly — **for $0**, using free/local tools only.

Works for any language (VoiceStudio OmniVoice: 646 languages; Edge TTS: 60+). Proven on kids content (Vietnamese) and Buddhist Dhamma videos (Thai).

## What it produces

```
topic / master.json  →  6–20+ scenes  →  final.mp4 (1280×720, crossfade, narration + music)
```

- **Images**: AI-generated scene art (AutoGLM Seedream or any OpenAI-compatible image API)
- **Text overlays**: Pillow (any Unicode font — works for Thai, Vietnamese, CJK…)
- **Voice-over**: local [VoiceStudio](https://github.com/debpalash/VoiceStudio) (free, offline, voice cloning, 646 languages) *or* Edge TTS (zero install)
- **Music**: built-in calm/cheerful synth (pure Python, no assets) *or* your own track
- **Assembly**: ffmpeg zoompan (Ken Burns) + crossfade + audio ducking
- **Verification (optional)**: faster-whisper sync check (narration vs scene windows)

## Requirements

- Python 3.10+ (`pip install -r requirements.txt`)
- **ffmpeg** on PATH
- One image backend and one TTS backend (see below) — **both can be free**

## Install

```bash
git clone https://github.com/<you>/zero-video-factory.git
cd zero-video-factory
pip install -r requirements.txt
```

## Quick start

1. Write a scene script `master.json` (see `examples/`):

```json
[
  {"id": 1, "prompt": "Golden Buddha statue in a Thai temple, digital painting, 16:9",
   "label": "ธรรมะ", "narration": "สวัสดีครับ เชิญทุกท่าน พักกาย พักใจ กับธรรมะก่อนนอน",
   "zoom": "in"},
  {"id": 2, "prompt": "A calm lake at dawn, mist, serene, digital painting, 16:9",
   "label": "ใจสงบ", "narration": "ใจที่สงบ ย่อมพบความสุข", "zoom": "out"}
]
```

2. Configure backends (copy `.env.example` → `.env`, or export env vars)
3. Build:

```bash
python build.py --config examples/dhamma/master.json --out out/my-video.mp4
```

## Backends

### Images

| Backend | Setup | Cost |
|---|---|---|
| `seedream` (default) | `IMAGE_BACKEND=seedream` + `SEEDREAM_APP_ID`, `SEEDREAM_APP_KEY` | free with AutoGLM creds |
| `openai` | `IMAGE_BACKEND=openai` + `OPENAI_BASE_URL`, `OPENAI_API_KEY` | depends on provider |

### TTS

| Backend | Setup | Cost | Languages |
|---|---|---|---|
| `voicestudio` (default) | install [VoiceStudio](https://github.com/debpalash/VoiceStudio), leave it running, set `VS_PROFILE_ID` | free, offline | 646 |
| `edge` | nothing | free | 60+ |

**Consistency tip**: VoiceStudio + a fixed `VS_PROFILE_ID` + `VS_SEED` (e.g. 42) produces the *same voice* across every scene — proven byte-identical with a fixed seed.

## Env reference

```
IMAGE_BACKEND=seedream|openai
SEEDREAM_APP_ID=
SEEDREAM_APP_KEY=
OPENAI_BASE_URL=
OPENAI_API_KEY=

TTS_BACKEND=voicestudio|edge
VS_API=http://localhost:3900
VS_PROFILE_ID=
VS_SEED=42
VS_STEPS=32
VS_SPEED=0.9
EDGE_VOICE=vi-VN-HoaiMyNeural

FONT_PATH=C:\Windows\Fonts\Tahoma.ttf
MUSIC_STYLE=calm|cheerful
MUSIC_TRACK=           # optional: your own wav/mp3
FPS=25
FADE=0.8
WIDTH=1280
HEIGHT=720
VERIFY=0               # 1 = run faster-whisper sync check
```

## Script format

`master.json` is an ordered list of scenes:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | scene number (1-based) |
| `prompt` | if no `reuse_image` | image generation prompt |
| `reuse_image` | if no `prompt` | reuse an existing image path |
| `label` | no | text overlay (bottom banner) |
| `narration` | yes | spoken text (any language) |
| `kind` | no | `intro` / `scene` / `outro` (affects padding) |
| `zoom` | no | `in` / `out` (Ken Burns direction) |

## Examples

- `examples/kids-balloons/` — Vietnamese kids colour-learning video (cheerful music, Vietnamese TTS)
- `examples/dhamma-thai/` — Thai Buddhist "listen before bed" video (calm music, Thai TTS)

## Verification

With `VERIFY=1`, the pipeline transcribes the final audio (faster-whisper) and reports how well each scene's narration matches its time window — catches wrong audio placement and hallucinated takes.

## License

MIT © 2026. Free to use, modify, and publish. **You are responsible for the content you generate** (voice cloning requires consent; respect others' copyright).

## Credits / disclaimer

- Images may use the AutoGLM Seedream endpoint if you have credentials; the code is a thin HTTP wrapper.
- TTS default relies on the open-source [VoiceStudio](https://github.com/debpalash/VoiceStudio) (AGPL-3.0 app; its models carry their own licenses).
- Edge TTS backend uses Microsoft's public endpoint — fine for personal use; check terms for commercial use.
