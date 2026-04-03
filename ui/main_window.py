from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem,
    QTextEdit, QDialog, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import threading
import sys
import webbrowser
import socket

from database.db import query
from core.counter_engine import run_counter_once
from ui.method_window import MethodWindow


# ================= LOG =================
class LogStream:
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, message):
        if message.strip():
            self.text_edit.append(message)

    def flush(self):
        pass


# ================= UNIT FORM =================
class UnitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Quản lý Đơn Vị")
        self.resize(500, 350)

        layout = QGridLayout()

        self.txt_code = QTextEdit()
        self.txt_name = QTextEdit()
        self.txt_address = QTextEdit()
        self.txt_ward = QTextEdit()
        self.txt_city = QTextEdit()
        self.txt_contact = QTextEdit()
        self.txt_phone = QTextEdit()

        layout.addWidget(QLabel("Mã Đơn Vị"), 0, 0)
        layout.addWidget(self.txt_code, 0, 1)

        layout.addWidget(QLabel("Tên Đơn Vị"), 1, 0)
        layout.addWidget(self.txt_name, 1, 1)

        layout.addWidget(QLabel("Địa chỉ"), 2, 0)
        layout.addWidget(self.txt_address, 2, 1)

        layout.addWidget(QLabel("Phường"), 3, 0)
        layout.addWidget(self.txt_ward, 3, 1)

        layout.addWidget(QLabel("Thành phố"), 4, 0)
        layout.addWidget(self.txt_city, 4, 1)

        layout.addWidget(QLabel("Người liên hệ"), 5, 0)
        layout.addWidget(self.txt_contact, 5, 1)

        layout.addWidget(QLabel("Điện thoại"), 6, 0)
        layout.addWidget(self.txt_phone, 6, 1)

        btn_save = QPushButton("💾 Lưu")
        btn_save.clicked.connect(self.save_data)
        layout.addWidget(btn_save, 7, 1)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        data = query("SELECT * FROM danh_muc_don_vi WHERE id_donvi = 1", fetch=True)
        if data:
            d = data[0]
            self.txt_code.setPlainText(d["code_don_vi"])
            self.txt_name.setPlainText(d["name_don_vi"])
            self.txt_address.setPlainText(d["address_don_vi"])
            self.txt_ward.setPlainText(d["ward_don_vi"])
            self.txt_city.setPlainText(d["city_don_vi"])
            self.txt_contact.setPlainText(d["contact_name"])
            self.txt_phone.setPlainText(str(d["contact_phone"]))

    def save_data(self):
        query("""
            UPDATE danh_muc_don_vi SET
                code_don_vi=?, name_don_vi=?, address_don_vi=?,
                ward_don_vi=?, city_don_vi=?,
                contact_name=?, contact_phone=?
            WHERE id_donvi=1
        """, (
            self.txt_code.toPlainText(),
            self.txt_name.toPlainText(),
            self.txt_address.toPlainText(),
            self.txt_ward.toPlainText(),
            self.txt_city.toPlainText(),
            self.txt_contact.toPlainText(),
            self.txt_phone.toPlainText()
        ))
        print("✅ Đã lưu đơn vị")
        self.accept()


# ================= MAIN =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QUẢN LÝ PHOTOCOPY")
        self.resize(1300, 750)

        self.init_ui()

        sys.stdout = LogStream(self.log_box)

        self.load_unit_info()
        self.load_machines()

        threading.Thread(target=run_counter_once, daemon=True).start()

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

        # RIGHT
        right_layout = QVBoxLayout()

        self.table_log = self.create_log_table()
        right_layout.addWidget(self.wrap_card(self.table_log))

        self.log_box = QTextEdit()
        self.log_box.setMaximumHeight(120)
        right_layout.addWidget(self.wrap_card(self.log_box))

        self.label_total = QLabel("Total: 0 | B/W: 0 | Color: 0")
        right_layout.addWidget(self.label_total)

        body.addLayout(right_layout, 1)

        layout.addLayout(body)
        main.setLayout(layout)

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
        header.setSectionResizeMode(QHeaderView.Interactive)

        # ✅ Cột Tên giãn mạnh (rất quan trọng)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 🔥 QUAN TRỌNG: click → load log
        table.cellClicked.connect(self.on_machine_selected)

        return table

    def create_log_table(self):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Time", "Total", "B/W", "Color", "Copy", "Scan"])
        table.horizontalHeader().setStretchLastSection(True)
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

            # ===== ONLINE =====
            online = self.check_online(ip)
            item_online = QTableWidgetItem("🟢" if online else "🔴")
            item_online.setTextAlignment(Qt.AlignCenter)
            self.table_machine.setItem(row, 3, item_online)

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

        for r, log in enumerate(logs):
            self.table_log.setItem(r, 0, QTableWidgetItem(log["timestamp"]))
            self.table_log.setItem(r, 1, QTableWidgetItem(str(log["total_counter"])))
            self.table_log.setItem(r, 2, QTableWidgetItem(str(log["bw_counter"])))
            self.table_log.setItem(r, 3, QTableWidgetItem(str(log["color_counter"])))
            self.table_log.setItem(r, 4, QTableWidgetItem(str(log["copy_counter"])))
            self.table_log.setItem(r, 5, QTableWidgetItem(str(log["scan_counter"])))

            total += log["total_counter"]
            bw += log["bw_counter"]
            color += log["color_counter"]

        self.label_total.setText(f"Total: {total} | B/W: {bw} | Color: {color}")

    # ================= UTILS =================
    def check_online(self, ip):
        try:
            socket.create_connection((ip, 80), timeout=1)
            return True
        except:
            return False