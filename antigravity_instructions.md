# Hướng Dẫn Dành Cho Antigravity (Dự án Photocopy Machine Agent)

Tài liệu này tổng hợp các quy tắc nghiêm ngặt từ `.cursorrules` và sở thích của người dùng để định hướng cách làm việc của Antigravity trong repository này.

## 1. Ngôn Ngữ Phản Hồi
- **Luôn luôn trả lời bằng tiếng Việt.**
- Phản hồi ngắn gọn, súc tích, đi thẳng vào vấn đề.

## 2. Kiến Trúc Dự Án (Architecture) - Phiên bản 2.1
Tuân thủ phân lớp chức năng:
- `core/engines`: Chứa các bộ tải dữ liệu (requests, selenium, v.v.). Mỗi file là một engine độc lập có hàm `fetch(url)`.
- `core/parsers`: Chứa các bộ phân tích dữ liệu HTML cho từng dòng máy.
- `database`: Quản lý SQLite. Sử dụng Migration khi thay đổi cấu trúc bảng.
- `ui`: Giao diện PySide6 (Sử dụng Signal/Slot để giao tiếp giữa các luồng).

## 3. Quy Tắc Lập Trình & Tính năng Mới (v2.1)

### Quản lý Cấu hình tập trung
- Các thông số `max_days` (Số ngày lưu log) và `times_per_day` (Tần suất quét) được quản lý tại bảng `danh_muc_don_vi`.
- Không lưu các thông số này tại bảng `machine` để đảm bảo tính nhất quán toàn hệ thống.

### Cơ chế Lập lịch tự động (Auto-Scheduling)
- Hệ thống tự động tính toán thời gian quét dựa trên công thức: `Interval = 8 giờ / times_per_day`.
- Sử dụng `QTimer` trong `main.py` để thực hiện việc quét định kỳ mà không làm treo UI.
- Luôn thực hiện dọn dẹp Log cũ (`cleanup_old_logs`) ngay khi khởi động chương trình.

### Hệ thống Plugin-based (Engine & Parser)
- Cả **Engine tải dữ liệu** và **Parser phân tích dữ liệu** đều được nạp động từ thư mục tương ứng (`core/engines/` và `core/parsers/`).
- Tên gọi trong database được xử lý **không phân biệt chữ hoa/thường** và tự động loại bỏ khoảng trắng.
- Tất cả các file trong các thư mục này BẮT BUỘC phải đặt tên bằng **chữ thường (lowercase)** để đảm bảo tính tương thích trên mọi hệ điều hành.

### Cơ chế Thử lại (Retry Mechanism)
- Khi việc lấy counter thất bại, hệ thống tự động chờ **10 giây** trước khi thử lại.
- Số lần thử lại tối đa là **3 lần**.

## 4. Cơ Chế Mở Rộng
- **Thêm Engine mới**: Tạo file tại `core/engines/{name}.py` với hàm `fetch(url)`.
- **Thêm Parser mới**: Tạo file tại `core/parsers/{name}.py` với hàm `parse(html)`.
- Các ComboBox trong giao diện cấu hình được thiết kế để tự động nhận diện các file mới này.

---
> [!IMPORTANT]
> Mọi thay đổi về Database phải đi kèm với cập nhật trong `database/init_db.py` và kịch bản Migration nếu đang có dữ liệu người dùng.
