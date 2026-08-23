# Contributing

Thanks for helping improve Zero-Cost Video Factory! 🎬

## Ways to contribute

- **Report bugs** — open an issue with the command you ran and the full error.
- **Add examples** — a `master.json` + short README for a new niche (kids, Dhamma, history, product explainers…) is hugely valuable. Include the `EDGE_VOICE`/`VS_PROFILE_ID` you used.
- **New backends** — TTS / image / music backends are small plug-ins (`pipeline/tts.py`, `pipeline/images.py`, `pipeline/music.py`). Keep the interface: `synthesize(cfg, text, out_path)`, `generate_image(cfg, prompt, out_path)`, `synth_music(cfg, duration, out_path)`.
- **Docs** — README translations are welcome (`README.vi.md` is the pattern).

## Dev setup

```bash
git clone https://github.com/wuangpei/zero-video-factory.git
cd zero-video-factory
pip install -r requirements.txt   # + edge-tts, faster-whisper for optional backends
```

## Pull request checklist

- [ ] One logical change per PR
- [ ] Works with the default free backends (seedream optional; edge TTS is the zero-install fallback)
- [ ] `.env` / secrets never committed (`.gitignore` covers it)
- [ ] `build.py --config examples/<your-example>/master.json` produces a video
