# Hướng Dẫn Dành Cho Antigravity (Dự án Photocopy Machine Agent)

Tài liệu này tổng hợp các quy tắc nghiêm ngặt từ `.cursorrules` và sở thích của người dùng để định hướng cách làm việc của Antigravity trong repository này.

## 1. Ngôn Ngữ Phản Hồi
- **Luôn luôn trả lời bằng tiếng Việt.**
- Phản hồi ngắn gọn, súc tích, đi thẳng vào vấn đề ("Không giải thích dài").

## 2. Kiến Trúc Dự Án (Architecture) - Phiên bản 2.0
Tuân thủ phân lớp chức năng:
- `core`: Xử lý logic lõi, parser, fetch dữ liệu.
- `database`: Thực hiện các truy vấn SQLite (Sử dụng `dict` thay vì `tuple`).
- `ui`: Giao diện PySide6 (Tuyệt đối không chứa logic xử lý nặng).
- `data`: Chứa database `agent.db` và các tệp nhật ký `logs`.

## 3. Quy Tắc Lập Trình Nghiêm Ngặt (Strict Rules)

### Phân Tách Lớp & Đa Luồng (Threading)
- Toàn bộ các tác vụ nặng (Fetch dữ liệu, Ping IP, Selenium) **BẮT BUỘC** phải chạy trong luồng riêng (`threading.Thread`).
- Tuyệt đối không để UI bị treo (freeze) khi đang xử lý dữ liệu.
- Sử dụng cơ chế `Signal/Slot` của PySide6 để truyền thông tin từ Worker Thread về giao diện chính.

### Cơ Chế Thanh Trạng Thái (Status Bar)
- Thay vì sử dụng hộp thoại thông báo (Popup), hệ thống sử dụng một `status_label` ở chân trang để báo cáo tiến trình.
- Hiển thị tiến trình chi tiết: `🚀 Lấy số counter máy {Tên} - IP: {IP} (x/n)`.
- Sử dụng màu sắc để phân biệt trạng thái: Cam (Đang chạy), Xanh lá (Hoàn tất), Trắng (Sẵn sàng).

### Parser & Fetch
- Mỗi dòng máy có Parser riêng trong `core/parsers/`.
- Tách riêng logic Fetch khỏi Parser.
- Xử lý Selenium thông minh: Có cơ chế "Hard Timeout" (45s) để chống treo trình duyệt ảo.

## 4. Cơ Chế Vận Hành & Mở Rộng (Plug-and-Play)
Hệ thống được thiết kế để thêm máy mới mà không cần sửa đổi code lõi:
- **Tự động hóa Log**: Tự động xóa file `.log` cũ hơn 30 ngày.
- **Thêm máy mới**:
    1. Tạo file parser mới tại `core/parsers/{Counter_Method}.py`.
    2. Khai báo trong bảng `danh_muc_method`.
    3. Thêm máy vào bảng `machine`.
- **Quét IP bất đồng bộ**: Khi tải danh sách máy, việc kiểm tra Online/Offline được thực hiện ngầm, không làm treo giao diện.

## 5. Cập nhật Phiên bản 2.0
- **UI**: Loại bỏ khung Log rườm rà, thay bằng Thanh trạng thái hiện đại.
- **Hiệu suất**: Quét IP bất đồng bộ, cập nhật icon Online ngay khi có kết quả.
- **Ổn định**: Khắc phục lỗi kẹt nút COUNTER bằng cơ chế Signal tập trung.

---
> [!IMPORTANT]
> Antigravity sẽ tự động áp dụng các quy tắc này cho mọi yêu cầu tiếp theo mà không cần nhắc lại.
