from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem,
    QTextEdit, QDialog, QHeaderView,
    QMessageBox, QLineEdit, QFormLayout, QGroupBox,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QCoreApplication
from PySide6.QtGui import QFont

import logging
import threading
import sys
import webbrowser

from database.db import query
from core.counter_engine import run_counter_once, is_ip_alive
from ui.method_window import MethodWindow

logger = logging.getLogger(__name__)


# ================= UNIT FORM =================
class UnitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Cấu Hình Thông Tin Đơn Vị")
        self.resize(550, 500)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        # Master Layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Style chung cho Dialog
        self.setStyleSheet("""
            QDialog { background-color: #f9f9f9; }
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #dcdcdc; 
                border-radius: 8px; 
                margin-top: 15px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #2b3a8a; }
            QLineEdit, QTextEdit { 
                border: 1px solid #ccc; 
                border-radius: 4px; 
                padding: 6px; 
                background: white;
            }
            QLineEdit:focus, QTextEdit:focus { border: 1px solid #2b3a8a; background: #f0f4ff; }
            QLabel { color: #555; }
        """)

        # --- NHÓM 1: THÔNG TIN ĐƠN VỊ ---
        group_org = QGroupBox("🏢 Thông Tin Tổ Chức")
        form_org = QFormLayout()
        form_org.setSpacing(10)
        form_org.setLabelAlignment(Qt.AlignLeft)

        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("Ví dụ: DV001")
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Tên đầy đủ của đơn vị/công ty")
        self.txt_address = QLineEdit()
        
        form_org.addRow("Mã Đơn Vị:", self.txt_code)
        form_org.addRow("Tên Đơn Vị:", self.txt_name)
        form_org.addRow("Địa Chỉ:", self.txt_address)

        self.txt_ward = QLineEdit()
        self.txt_ward.setPlaceholderText("Phường/Xã")
        self.txt_city = QLineEdit()
        self.txt_city.setPlaceholderText("Quận/Huyện - Tỉnh/TP")

        form_org.addRow("Phường/Xã:", self.txt_ward)
        form_org.addRow("Tỉnh/Thành:", self.txt_city)

        group_org.setLayout(form_org)
        layout.addWidget(group_org)

        # --- NHÓM 2: THÔNG TIN LIÊN HỆ ---
        group_contact = QGroupBox("📞 Người Đại Diện / Liên Hệ")
        form_contact = QFormLayout()
        form_contact.setSpacing(10)

        self.txt_contact = QLineEdit()
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("Số điện thoại liên lạc")

        form_contact.addRow("Người Liên Hệ:", self.txt_contact)
        form_contact.addRow("Điện Thoại:", self.txt_phone)

        group_contact.setLayout(form_contact)
        layout.addWidget(group_contact)

        layout.addStretch()

        # --- BUTTONS ---
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("  Lưu Cấu Hình")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2b3a8a;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #3d4fb3; }
            QPushButton:pressed { background-color: #1a255e; }
        """)
        self.btn_save.clicked.connect(self.save_data)

        self.btn_cancel = QPushButton("Đóng")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setFixedWidth(100)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_data(self):
        data = query("SELECT * FROM danh_muc_don_vi WHERE id_donvi = 1", fetch=True)
        if data:
            d = data[0]
            self.txt_code.setText(d["code_don_vi"])
            self.txt_name.setText(d["name_don_vi"])
            self.txt_address.setText(d["address_don_vi"])
            self.txt_ward.setText(d["ward_don_vi"])
            self.txt_city.setText(d["city_don_vi"])
            self.txt_contact.setText(d["contact_name"])
            self.txt_phone.setText(str(d["contact_phone"]))

    def save_data(self):
        query("""
            UPDATE danh_muc_don_vi SET
                code_don_vi=?, name_don_vi=?, address_don_vi=?,
                ward_don_vi=?, city_don_vi=?,
                contact_name=?, contact_phone=?
            WHERE id_donvi=1
        """, (
            self.txt_code.text(),
            self.txt_name.text(),
            self.txt_address.text(),
            self.txt_ward.text(),
            self.txt_city.text(),
            self.txt_contact.text(),
            self.txt_phone.text()
        ))
        msg = QMessageBox(self)
        msg.setWindowTitle("Thông báo")
        msg.setText("✅ Cập nhật thông tin đơn vị thành công!")
        msg.exec()
        self.accept()


# ================= MAIN =================
class MainWindow(QMainWindow):
    # Khai báo Signal để truyền tin từ thread khác về UI
    progress_signal = Signal(str) 

    def __init__(self):
        super().__init__()

        self.setWindowTitle("QUẢN LÝ PHOTOCOPY")
        self.resize(1300, 750)

        self.init_ui()

        # Kết nối Signal với hàm xử lý thông minh
        self.progress_signal.connect(self._handle_status_update)

        sys.stdout = sys.__stdout__ # Khôi phục stdout chuẩn

        self.load_unit_info()
        self.load_machines()

    # ================= UI =================
    def init_ui(self):
        main = QWidget()
        self.setCentralWidget(main)

        main.setStyleSheet("""
            QMainWindow { background:#f5f6fa; }
            QLabel { font-size:13px; }
            QTableWidget { background:white; border:1px solid #ccc; }
            QHeaderView::section {
                background:#e9edf5;
                padding:6px;
                border:1px solid #ddd;
                font-weight:bold;
            }
            QPushButton {
                background:#e0e0e0;
                border:1px solid #888;
                padding:6px 12px;
                border-radius:4px;
            }
            QPushButton:hover { background:#d0d0d0; }
        """)

        layout = QVBoxLayout()

        # HEADER
        header = QHBoxLayout()
        title = QLabel("QUẢN LÝ PHOTOCOPY")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color:#2b3a8a;")

        header.addWidget(title)
        header.addStretch()

        self.btn_donvi = QPushButton("ĐƠN VỊ")
        self.btn_machine = QPushButton("MÁY")
        self.btn_method = QPushButton("METHOD")
        self.btn_counter = QPushButton("COUNTER")
        self.btn_exit = QPushButton("THOÁT")

        for b in [self.btn_donvi, self.btn_machine, self.btn_method, self.btn_counter, self.btn_exit]:
            header.addWidget(b)

        
        self.btn_donvi.clicked.connect(self.open_unit_dialog)
        self.btn_machine.clicked.connect(self.open_machine_window)
        self.btn_method.clicked.connect(self.open_method_window)
        self.btn_counter.clicked.connect(self.trigger_counter) # <-- Thêm dòng này
        self.btn_exit.clicked.connect(self.close)

        layout.addLayout(header)

        # ===== UNIT DASHBOARD =====
        unit_box = QWidget()
        unit_box.setStyleSheet("""
            background:white;
            border:1px solid #ddd;
            border-radius:6px;
            padding:10px;
        """)

        unit_layout = QGridLayout()
        unit_layout.setHorizontalSpacing(40)

        self.lb_line1_left = QLabel("")
        self.lb_line1_right = QLabel("")
        self.lb_line2_left = QLabel("")
        self.lb_line2_right = QLabel("")

        unit_layout.addWidget(self.lb_line1_left, 0, 0)
        unit_layout.addWidget(self.lb_line1_right, 0, 1)
        unit_layout.addWidget(self.lb_line2_left, 1, 0)
        unit_layout.addWidget(self.lb_line2_right, 1, 1)

        unit_layout.setColumnStretch(0, 1)
        unit_layout.setColumnStretch(1, 1)

        unit_box.setLayout(unit_layout)
        layout.addWidget(unit_box)

        # BODY
        body = QHBoxLayout()

        # LEFT
        self.table_machine = self.create_machine_table()
        body.addWidget(self.wrap_card(self.table_machine), 1)

        # ===== RIGHT =====
        from PySide6.QtWidgets import QSplitter
        from PySide6.QtCore import Qt

        right_layout = QVBoxLayout()  # <-- Thêm lại dòng này

        # Table log
        self.table_log = self.create_log_table() 
        self.table_log.keyPressEvent = self.log_table_keypress 

        # 👉 Wrap lại (giữ style card cũ)
        log_table_widget = self.wrap_card(self.table_log)
        right_layout.addWidget(log_table_widget)

        # Thanh trạng thái (Status Bar) thay cho label cũ
        self.status_label = QLabel(" ⚪ Sẵn sàng")
        self.status_label.setMinimumHeight(35)
        self.status_label.setStyleSheet("""
            background: #ffffff;
            border: 1px solid #dcdcdc;
            padding-left: 10px;
            font-weight: bold;
            color: #555;
            border-bottom-left-radius: 6px;
            border-bottom-right-radius: 6px;
        """)
        right_layout.addWidget(self.status_label)

        body.addLayout(right_layout, 1)

        layout.addLayout(body)
        main.setLayout(layout)

    # ================= TRIGGER COUNTER =================
    def trigger_counter(self):
        """Khởi chạy quá trình lấy counter trong thread riêng."""
        # Chặn nếu đang chạy
        if not self.btn_counter.isEnabled():
            return

        self.btn_counter.setEnabled(False) 
        self.status_label.setStyleSheet("background: #fff4e6; color: #d9480f; font-weight: bold; padding-left:10px;")
        
        thread = threading.Thread(target=self._run_counter_logic, daemon=True)
        thread.start()

    def _run_counter_logic(self):
        try:
            # Truyền callback để phát Signal
            run_counter_once(
                on_machine_finished=self._report_machine_online,
                on_progress=lambda msg: self.progress_signal.emit(f" 🔍 {msg}")
            )
        except Exception as e:
            logger.error("Lỗi thực thi counter: %s", e)
            self.progress_signal.emit(f" ❌ Lỗi: {str(e)}")
        finally:
            # Phát tín hiệu báo kết thúc để UI khôi phục nút bấm
            self.progress_signal.emit("FINISH_PROCESS")

    def _handle_status_update(self, msg):
        """Xử lý tín hiệu trả về: cập nhật text status hoặc cập nhật icon IP hoặc kết thúc."""
        if msg == "FINISH_PROCESS":
            self._on_counter_finished()
        elif msg.startswith("UPDATE_IP:"):
            try:
                _, row, icon = msg.split(":")
                item = QTableWidgetItem(icon)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_machine.setItem(int(row), 3, item)
            except: pass
        else:
            self.status_label.setText(msg)

    def _report_machine_online(self, code_machine, is_online):
        """Được gọi từ thread khác để cập nhật icon Online."""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._update_row_online(code_machine, is_online))

    def _update_row_online(self, code_machine, is_online):
        """Cập nhật icon xanh/đỏ cho một dòng cụ thể trên bảng."""
        for row in range(self.table_machine.rowCount()):
            item = self.table_machine.item(row, 0)
            if item and item.text() == code_machine:
                icon = "🟢" if is_online else "🔴"
                item_online = QTableWidgetItem(icon)
                item_online.setTextAlignment(Qt.AlignCenter)
                self.table_machine.setItem(row, 3, item_online)
                break

    def _on_counter_finished(self):
        # 🟢 1. Khôi phục nút bấm ngay lập tức
        self.btn_counter.setEnabled(True)
        self.btn_counter.setText("COUNTER")
        self.status_label.setStyleSheet("background: #d4edda; color: #155724; font-weight: bold; padding-left:10px;")
        self.status_label.setText(" ✅ Hoàn tất chu trình lấy counter.")
        
        # 🟢 2. Ép hệ thống vẽ lại giao diện nút bấm
        QCoreApplication.processEvents()
        
        # 3. Reload danh sách máy (chạy ngầm)
        self.load_machines() 
        
        # 4. Cập nhật log máy đang chọn
        current_row = self.table_machine.currentRow()
        if current_row != -1:
            code = self.table_machine.item(current_row, 0).text()
            self.load_logs(code)
            
        logger.info("✅ Quá trình lấy counter hoàn tất.")

    # ===== WRAP CARD =====
    def wrap_card(self, widget):
        box = QWidget()
        box.setStyleSheet("""
            background:white;
            border:1px solid #ddd;
            border-radius:6px;
        """)
        lay = QVBoxLayout()
        lay.setContentsMargins(8, 8, 8, 8)
        lay.addWidget(widget)
        box.setLayout(lay)
        return box

    # ================= UNIT =================
    def load_unit_info(self):
        data = query("SELECT * FROM danh_muc_don_vi WHERE id_donvi=1", fetch=True)
        if not data:
            return

        d = data[0]

        self.lb_line1_left.setText(f"MS Đơn Vị : {d['code_don_vi']}")
        self.lb_line1_right.setText(f"Tên Đơn Vị : {d['name_don_vi']}")

        contact = f"{d['contact_name']} - {d['contact_phone']}"
        self.lb_line2_left.setText(f"Liên Hệ : {contact}")

        addr = f"{d['address_don_vi']} - {d['ward_don_vi']} - {d['city_don_vi']}"
        self.lb_line2_right.setText(f"Địa Chỉ : {addr}")

    def open_unit_dialog(self):
        dlg = UnitDialog(self)
        if dlg.exec():
            self.load_unit_info()

    # ================= OPEN METHOD =================
    def open_method_window(self):
        dlg = MethodWindow()
        dlg.exec()

    # ================= OPEN machine =================
    def open_machine_window(self):
        from ui.machine_window import MachineWindow
        dlg = MachineWindow()
        dlg.exec()
        self.load_machines()  # reload sau khi đóng

    # ================= MACHINE =================
    from PySide6.QtWidgets import QHeaderView

    def create_machine_table(self):
        table = QTableWidget()
        table.setColumnCount(7)

        table.setHorizontalHeaderLabels([
            "Mã", "Tên Máy", "IP",
            "Online", "Xem",
            "Vị trí", "Counter"
        ])

        header = table.horizontalHeader()

        # ✅ Cho resize tự do
        header = table.horizontalHeader()

        # 👉 Cho resize tự do toàn bộ
        header.setSectionResizeMode(QHeaderView.Interactive)

        # 👉 Cột nhỏ → fit nội dung
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Mã
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Tên máy
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # IP
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Online
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Xem
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Vị trí
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Counter

        # 👉 Cột quan trọng → rộng mặc định + vẫn resize được
        #header.resizeSection(1, 250)  # Tên máy
        #header.resizeSection(5, 220)  # Vị trí
    
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 🔥 QUAN TRỌNG: click → load log
        table.cellClicked.connect(self.on_machine_selected)

        return table

    # ================= LOG =================

    def create_log_table(self):
        table = QTableWidget()
        table.setColumnCount(7)

        table.setHorizontalHeaderLabels([
            "Time", "Total", "B/W",
            "Color", "Copy", "Scan",
            "RAW"
        ])

        header = table.horizontalHeader()

        # 👉 Cho resize tự do
        header.setSectionResizeMode(QHeaderView.Interactive)

        # 👉 Cột nhỏ auto fit
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        # 👉 Time rộng hơn
        header.resizeSection(0, 140)

        # 👉 Cho phép chọn nhieu dòng
        table.setSelectionMode(QTableWidget.ExtendedSelection)  # chọn nhiều dòng
        table.setSelectionBehavior(QTableWidget.SelectRows)

        return table

    def load_machines(self):
        machines = query("SELECT * FROM machine", fetch=True)
        self.table_machine.setRowCount(len(machines))

        for row, m in enumerate(machines):
            code = m["code_machine"]
            name = m["name_machine"]
            ip = m["ip_machine"]
            path = m["path_machine"]
            location = m["location"] or ""
            enabled = m["counter_enabled"]

            # ===== TEXT =====
            self.table_machine.setItem(row, 0, QTableWidgetItem(code))
            self.table_machine.setItem(row, 1, QTableWidgetItem(name))
            self.table_machine.setItem(row, 2, QTableWidgetItem(ip))

            # ===== ONLINE (Quét bất đồng bộ) =====
            item_status = QTableWidgetItem("⚪")
            item_status.setTextAlignment(Qt.AlignCenter)
            self.table_machine.setItem(row, 3, item_status)
            
            # Gửi yêu cầu quét ngầm
            from PySide6.QtCore import QTimer
            QTimer.singleShot(row * 100, lambda r=row, i=ip: self._async_check_online(r, i))

            # ===== BUTTON XEM =====

            # ===== BUTTON XEM =====
            url = f"http://{ip}{path}"
            btn = QPushButton("Xem")
            btn.setToolTip(url)
            btn.clicked.connect(lambda _, u=url: webbrowser.open(u))
            self.table_machine.setCellWidget(row, 4, btn)

            # ===== LOCATION =====
            self.table_machine.setItem(row, 5, QTableWidgetItem(location))

            # ===== COUNTER ENABLED =====
            item_counter = QTableWidgetItem("✔️" if enabled else "❌")
            item_counter.setTextAlignment(Qt.AlignCenter)

            self.table_machine.setItem(row, 6, item_counter)

    # ================= LOG =================
    def on_machine_selected(self, row, col):
        code = self.table_machine.item(row, 0).text()
        self.load_logs(code)

    def load_logs(self, code):
        logs = query("""
            SELECT * FROM counter_log
            WHERE code_machine=?
            ORDER BY timestamp DESC
            LIMIT 50
        """, (code,), fetch=True)

        self.table_log.setRowCount(len(logs))

        total = bw = color = 0

        from datetime import datetime

        for r, log in enumerate(logs):
            # ===== FORMAT TIME =====
            try:
                dt = datetime.fromisoformat(log["timestamp"])
                time_str = dt.strftime("%d/%m/%y %H:%M")
            except ValueError:
                logger.warning("Cannot parse timestamp: %s", log["timestamp"])
                time_str = log["timestamp"]

            item_time = QTableWidgetItem(time_str)
            item_time.setData(Qt.UserRole, log["timestamp"])  # 👈 lưu timestamp gốc
            self.table_log.setItem(r, 0, item_time)

            self.table_log.setItem(r, 1, QTableWidgetItem(str(log["total_counter"])))
            self.table_log.setItem(r, 2, QTableWidgetItem(str(log["bw_counter"])))
            self.table_log.setItem(r, 3, QTableWidgetItem(str(log["color_counter"])))
            self.table_log.setItem(r, 4, QTableWidgetItem(str(log["copy_counter"])))
            self.table_log.setItem(r, 5, QTableWidgetItem(str(log["scan_counter"])))

            # ===== RAW BUTTON =====
            raw_data = log.get("raw_counter", "")

            widget = QWidget()
            lay = QHBoxLayout()
            lay.setContentsMargins(2, 2, 2, 2)

            btn_txt = QPushButton("TXT")
            btn_web = QPushButton("WEB")

            # TXT → popup text
            btn_txt.clicked.connect(lambda _, d=raw_data: self.show_raw_text(d))

            # WEB → mở browser (nếu raw là html/url)
            btn_web.clicked.connect(lambda _, d=raw_data: self.open_raw_web(d))

            lay.addWidget(btn_txt)
            lay.addWidget(btn_web)

            widget.setLayout(lay)

            self.table_log.setCellWidget(r, 6, widget)

            # ===== TOTAL =====
            total += log["total_counter"]
            bw += log["bw_counter"]
            color += log["color_counter"]

    # ================= UTILS =================
    def _async_check_online(self, row, ip):
        """Kiểm tra IP và cập nhật đúng dòng trên table mà không block UI."""
        def task():
            online = self.check_online(ip)
            icon = "🟢" if online else "🔴"
            # Cập nhật lại UI từ thread
            self.progress_signal.emit(f"UPDATE_IP:{row}:{icon}")
            
        threading.Thread(target=task, daemon=True).start()

    def check_online(self, ip):
        # Tăng timeout lên 2.5s để tránh báo Offline nhầm do mạng chậm
        return is_ip_alive(ip, timeout=2.5)
        
    # =================== Hien thi RAW DANG TEXT=================
    def show_raw_text(self, raw):
        dlg = QDialog(self)
        dlg.setWindowTitle("RAW TEXT")
        dlg.resize(800, 600)

        layout = QVBoxLayout()
        txt = QTextEdit()
        txt.setPlainText(str(raw) if raw else "Không có dữ liệu")
        layout.addWidget(txt)

        dlg.setLayout(layout)
        dlg.exec()

    # =================== Hien thi RAW DANG WEB (HTML/URL) =================
    def open_raw_web(self, raw):
        if not raw:
            return

        import tempfile
        import os

        # 👉 Ghi HTML ra file tạm
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
        tmp_file.write(raw)
        tmp_file.close()

        # 👉 Mở bằng browser
        webbrowser.open(f"file:///{tmp_file.name}")

    # =================== nhấn delete log ===================
    def log_table_keypress(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_logs()
        else:
            QTableWidget.keyPressEvent(self.table_log, event)

    # =================== Xóa log đã chọn ===================
    def delete_selected_logs(self):
        selected_rows = set()

        for item in self.table_log.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            return

        # 👉 confirm
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa {len(selected_rows)} dòng đã chọn?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 👉 lấy code_machine hiện tại
        current_row = self.table_machine.currentRow()
        if current_row == -1:
            return

        code_machine = self.table_machine.item(current_row, 0).text()

        # 👉 xóa theo timestamp (giả sử unique)
        for row in selected_rows:
            timestamp = self.table_log.item(row, 0).data(Qt.UserRole)

            # ⚠ convert lại format nếu cần
            query("""
                DELETE FROM counter_log
                WHERE code_machine=? AND timestamp=?
            """, (code_machine, timestamp))

        # reload lại
        self.load_logs(code_machine)

        print(f"🗑️ Đã xóa {len(selected_rows)} dòng log")   