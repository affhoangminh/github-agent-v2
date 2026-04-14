# Hướng Dẫn Dành Cho Antigravity (Dự án Photocopy Machine Agent)

Tài liệu này tổng hợp các quy tắc nghiêm ngặt từ `.cursorrules` và sở thích của người dùng để định hướng cách làm việc của Antigravity trong repository này.

## 1. Ngôn Ngữ Phản Hồi
- **Luôn luôn trả lời bằng tiếng Việt.**
- Phản hồi ngắn gọn, súc tích, đi thẳng vào vấn đề ("Không giải thích dài").

## 2. Kiến Trúc Dự Án (Architecture)
Tuân thủ phân lớp chức năng:
- `core`: Xử lý logic lõi, parser, fetch dữ liệu.
- `services`: Điều phối business logic (nơi duy nhất thực hiện việc này).
- `database`: Thực hiện các truy vấn SQLite.
- `ui`: Giao diện PySide6 (Tuyệt đối không chứa business logic).
- `utils`: Các hàm trợ giúp.

## 3. Quy Tắc Lập Trình Nghiêm Ngặt (Strict Rules)

### Phân Tách Lớp (Layer Separation)
- UI không được chứa logic nghiệp vụ.
- Parser không được gọi trực tiếp đến database.

### Parser & Fetch
- Mỗi hãng máy photocopy phải có một parser riêng.
- Parser chỉ trả về dictionary theo định dạng: `{"total": int, "bw": int, "color": int}`.
- Tách riêng logic Fetch (HTTP / Selenium) ra khỏi Parser. Không viết request trực tiếp trong parser.

### Database
- Không truy cập dữ liệu qua chỉ số (e.g., `machine[5]`).
- Bắt buộc dùng key (e.g., `machine["ip"]`).
- Sử dụng `sqlite3.Row` factory.

### Xử Lý Lỗi & Naming
- Không sử dụng `except:` trống (bare except).
- Bắt buộc phải logging lỗi để debug.
- Naming: `snake_case` cho hàm/biến, `PascalCase` cho class.

### Giới Hạn & Tối Ưu
- Mỗi hàm không được quá 50 dòng.
- Không lặp lại logic (DRY - Don't Repeat Yourself).
- Tái sử dụng code cũ tối đa.

## 4. Quy Tắc Đầu Ra (Output)
- Code phải sạch, dễ đọc.
- Chỉ trả về các file cần sửa đổi.
- Ưu tiên hiển thị diff rõ ràng.

---
> [!IMPORTANT]
> Antigravity sẽ tự động áp dụng các quy tắc này cho mọi yêu cầu tiếp theo mà không cần nhắc lại.
