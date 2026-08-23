# Bộ trả lời bình luận — Zero-Cost Video Factory (post Facebook)

## 💬 Cài đặt kiểu gì / khó không?
> Cài rất dễ: `pip install -r requirements.txt` + cài ffmpeg là xong. Rồi copy file master.json mẫu, sửa lời thoại, chạy `python build.py --config examples/.../master.json --out video.mp4`. Mình có README tiếng Việt nữa, kèm 3 ví dụ mẫu chạy được luôn 👍

## 💬 Có tốn tiền không?
> $0 hoàn toàn! Ảnh AI miễn phí, giọng đọc chạy local (VoiceStudio mở mã nguồn, 646 ngôn ngữ) hoặc Edge TTS, nhạc nền tự sinh bằng code. Không cần key API bắt buộc nào.

## 💬 Tiếng Việt/Thái/Anh được không?
> Được hết! Mình làm thử cả video thiếu nhi tiếng Việt lẫn video Phật pháp tiếng Thái trên chính pipeline này. VoiceStudio hỗ trợ 646 ngôn ngữ.

## 💬 Cần GPU mạnh không?
> Không bắt buộc. Chạy CPU được (chậm hơn thôi). Có GPU NVIDIA thì giọng đọc nhanh hơn nhiều — mình dùng GTX 1080 là mượt.

## 💬 Clone giọng được không?
> Được! VoiceStudio có clone giọng: chỉ cần 3-15 giây mẫu ghi âm, tạo profile rồi dùng cho cả video. Giọng đồng nhất nhờ seed cố định.

## 💬 Làm video dài (30-60 phút) được không?
> Được, chỉ tốn thời gian máy thôi: video 1 tiếng ~ 6-7 giờ máy chạy tự động (chủ yếu là lồng tiếng + dựng). Chạy qua đêm là xong.

## 💬 Repo dùng API gì? Có an toàn không?
> Chạy local là chính. Backend ảnh có thể dùng AutoGLM Seedream (miễn phí) hoặc bất kỳ API tương thích OpenAI. Không gửi dữ liệu đi đâu nếu không muốn.

## 💬 Khen / cảm ơn
> Cảm ơn bạn! Nếu thấy hữu ích thì star + góp ý giúp mình nhé — mình rất cần feedback để cải thiện 🙏

## 💬 Góp ý / báo lỗi
> Cảm ơn feedback! Bạn mở issue trên GitHub giúp mình với ạ (kèm lệnh đã chạy + log lỗi) — mình xử lý nhanh. Hoặc tạo PR luôn cũng được, CONTRIBUTING.md hướng dẫn sẵn 👍

---

## 📌 Mẹo khi trả lời
- Luôn kèm link repo khi trả lời: https://github.com/wuangpei/zero-video-factory
- Nếu có video promo, đính kèm lại cho người hỏi
- Trả lời nhanh + thân thiện → thuật toán ưu tiên, tăng tương tác
