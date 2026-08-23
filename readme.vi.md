# Zero-Cost Video Factory

[![CI](https://github.com/wuangpei/zero-video-factory/actions/workflows/ci.yml/badge.svg)](https://github.com/wuangpei/zero-video-factory/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Biến một chủ đề thành video lồng tiếng hoàn chỉnh — ảnh, giọng đọc, nhạc nền, phụ đề và ghép video — **với chi phí $0**, chỉ dùng công cụ miễn phí/local.

Hỗ trợ đa ngôn ngữ (VoiceStudio OmniVoice: 646 ngôn ngữ; Edge TTS: 60+). Đã kiểm chứng trên nội dung thiếu nhi (tiếng Việt) và video Phật pháp (tiếng Thái).

## Pipeline tạo ra gì

```
chủ đề / master.json  →  6–20+ cảnh  →  final.mp4 (1280×720, crossfade, lồng tiếng + nhạc)
```

- **Ảnh**: sinh bằng AI (AutoGLM Seedream hoặc mọi API ảnh tương thích OpenAI)
- **Chữ overlay**: Pillow (font Unicode — chạy được Thái, Việt, CJK…)
- **Giọng đọc**: [VoiceStudio](https://github.com/debpalash/VoiceStudio) local (miễn phí, offline, clone giọng, 646 ngôn ngữ) *hoặc* Edge TTS (không cần cài gì)
- **Nhạc nền**: synth sẵn (calm/cheerful, Python thuần — không cần asset) *hoặc* nhạc của bạn
- **Ghép video**: ffmpeg zoompan (hiệu ứng Ken Burns) + crossfade + trộn âm thanh
- **Kiểm tra độ khớp (tùy chọn)**: faster-whisper đối chiếu lời thoại với từng cảnh

## Yêu cầu

- Python 3.10+ (`pip install -r requirements.txt`)
- **ffmpeg** trong PATH
- Một backend ảnh + một backend TTS (xem dưới) — **cả hai đều có thể miễn phí**

## Cài đặt

```bash
git clone https://github.com/wuangpei/zero-video-factory.git
cd zero-video-factory
pip install -r requirements.txt
```

## Bắt đầu nhanh

1. Viết kịch bản `master.json` (xem `examples/`):

```json
[
  {"id": 1, "prompt": "Golden Buddha statue in a Thai temple, digital painting, 16:9",
   "label": "ธรรมะ", "narration": "สวัสดีครับ เชิญทุกท่าน พักกาย พักใจ กับธรรมะก่อนนอน",
   "zoom": "in"},
  {"id": 2, "prompt": "A calm lake at dawn, mist, serene, digital painting, 16:9",
   "label": "ใจสงบ", "narration": "ใจที่สงบ ย่อมพบความสุข", "zoom": "out"}
]
```

2. Cấu hình backend (copy `.env.example` → `.env`, hoặc export biến môi trường)
3. Dựng video:

```bash
python build.py --config examples/dhamma-thai/master.json --out out/video-cua-toi.mp4
```

## Backend

### Ảnh

| Backend | Cài đặt | Chi phí |
|---|---|---|
| `seedream` (mặc định) | `IMAGE_BACKEND=seedream` + `SEEDREAM_APP_ID`, `SEEDREAM_APP_KEY` | miễn phí với credential AutoGLM |
| `openai` | `IMAGE_BACKEND=openai` + `OPENAI_BASE_URL`, `OPENAI_API_KEY` | tùy nhà cung cấp |

### Giọng đọc

| Backend | Cài đặt | Chi phí | Ngôn ngữ |
|---|---|---|---|
| `voicestudio` (mặc định) | cài [VoiceStudio](https://github.com/debpalash/VoiceStudio), để app chạy, đặt `VS_PROFILE_ID` | miễn phí, offline | 646 |
| `edge` | không cần gì | miễn phí | 60+ |

**Mẹo đồng nhất giọng**: VoiceStudio + `VS_PROFILE_ID` cố định + `VS_SEED` (vd 42) cho ra **cùng một giọng** ở mọi cảnh — đã chứng minh file byte-identical khi seed cố định.

## Tham chiếu biến môi trường

```
IMAGE_BACKEND=seedream|openai
SEEDREAM_APP_ID=
SEEDREAM_APP_KEY=
***
OPENAI_API_KEY=

TTS_BA…edge
VS_API=http://localhost:3900
VS_PROFILE_ID=
VS_SEED=42
VS_STEPS=32
VS_SPEED=0.9
EDGE_VOICE=vi-VN-HoaiMyNeural

FONT_PATH=C:\Windows\Fonts\Tahoma.ttf
MUSIC_STYLE=calm|cheerful
MUSIC_TRACK=
FPS=25
FADE=0.8
WIDTH=1280
HEIGHT=720
VERIFY=0
```

## Định dạng kịch bản

`master.json` là danh sách cảnh theo thứ tự:

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `id` | có | số thứ tự cảnh (bắt đầu 1) |
| `prompt` | nếu không có `reuse_image` | prompt sinh ảnh |
| `reuse_image` | nếu không có `prompt` | dùng lại ảnh có sẵn |
| `label` | không | chữ overlay (banner dưới) |
| `narration` | có | lời thoại (ngôn ngữ bất kỳ) |
| `kind` | không | `intro` / `scene` / `outro` (ảnh hưởng padding) |
| `zoom` | không | `in` / `out` (hướng Ken Burns) |

## Ví dụ

- `examples/kids-balloons/` — video học màu cho trẻ em (nhạc vui, tiếng Việt)
- `examples/dhamma-thai/` — video Phật pháp tiếng Thái "nghe trước khi ngủ" (nhạc thiền, tiếng Thái)
- `examples/dhamma-sleep/` — phiên bản 20 cảnh đầy đủ (4 chủ đề: สติ · ปล่อยวาง · กรรม · ความสุข)

## Kiểm tra độ khớp

Với `VERIFY=1`, pipeline tự transcribe audio cuối (faster-whisper) và báo % khớp lời thoại của từng cảnh với cửa sổ thời gian — bắt được lỗi đặt sai âm thanh và đoạn bị "ảo giác" (hallucinate).

## Giấy phép

MIT © 2026. Tự do dùng, sửa, phát hành. **Bạn chịu trách nhiệm về nội dung mình tạo** (clone giọng cần sự đồng ý; tôn trọng bản quyền người khác).

## Ghi chú / nguồn

- Ảnh có thể dùng endpoint AutoGLM Seedream nếu bạn có credential; code chỉ là wrapper HTTP mỏng.
- TTS mặc định dựa trên [VoiceStudio](https://github.com/debpalash/VoiceStudio) mã nguồn mở (app AGPL-3.0; model giữ license riêng).
- Backend Edge TTS dùng endpoint công khai của Microsoft — phù hợp dùng cá nhân; kiểm tra điều khoản nếu dùng thương mại.
