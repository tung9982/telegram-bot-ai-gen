# Telegram Bot AI Gen

Phần mềm trong dự án đã được bổ sung một module mới giúp tạo mockup áo thun bằng AI dựa trên prompt mô tả.

## Tính năng chính

- Sinh artwork bằng mô hình Stable Diffusion (có thể dùng `stabilityai/stable-diffusion-xl-base-1.0` hoặc bất kỳ checkpoint tương thích).
- Tự động ghép artwork vào mockup áo thun với khả năng chọn màu áo và nền.
- Hỗ trợ sử dụng artwork có sẵn mà không cần sinh mới.
- Cấu hình được số bước suy luận, guidance scale, seed… để kiểm soát chất lượng ảnh.

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate  # Windows dùng .venv\\Scripts\\activate
pip install -r requirements.txt
```

Một số mô hình diffusion cần GPU để chạy nhanh. Nếu bạn sử dụng CPU hãy đảm bảo máy có đủ RAM và cân nhắc giảm kích thước ảnh.

## Sử dụng dòng lệnh

Tập lệnh chính nằm tại `src/app.py`.

```bash
python -m src.app "cyberpunk tiger illustration"
```

Các tuỳ chọn phổ biến:

- `--negative-prompt` – loại bỏ chi tiết không mong muốn.
- `--shirt-color` – mã màu hex cho màu áo, ví dụ `#111827`.
- `--background-color` – mã màu hex nền mockup.
- `--steps` – số bước suy luận Stable Diffusion.
- `--guidance-scale` – mức độ bám prompt.
- `--seed` – giúp tái tạo lại kết quả.
- `--design` – đường dẫn tới file artwork có sẵn, khi đó chương trình chỉ ghép mockup.

Kết quả sẽ được lưu trong thư mục `outputs/` (hoặc đường dẫn bạn chỉ định qua `--output` và `--design-output`).

## Tự động hoá hoặc nhúng vào dịch vụ khác

Bạn có thể nhập trực tiếp `MockupGenerator` từ gói `mockup_ai`:

```python
from mockup_ai import MockupGenerator, MockupRequest

generator = MockupGenerator(device="cuda")
request = MockupRequest(
    prompt="watercolor koi fish, japanese waves, white t-shirt",
    shirt_color="#FFFFFF",
    background_color="#e5e7eb",
)
result = generator.generate(request)
print("Design:", result.design_path)
print("Mockup:", result.mockup_path)
```

Module này có thể tích hợp vào workflow sẵn có trên Telegram Bot hoặc các công cụ tự động hoá như n8n.
