from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QTextEdit, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal

import requests

from database.db import query
from ui.method_window import MethodWindow
from core.engine import parse_counter


# ================= THREAD =================
class FetchWorker(QThread):
    finished = Signal(dict)

    def __init__(self, machine, method):
        super().__init__()
        self.machine = machine
        self.method = method

    def run(self):
        try:
            ip = self.machine[5]
            url = self.machine[6]
            full_url = f"http://{ip}{url}"

            response = requests.get(full_url, timeout=5)
            raw = response.text

            parser_name = self.method[5]
            counter = parse_counter(raw, parser_name)

            result = {
                "status": "OK",
                "raw": raw,
                "counter": counter,
            }

        except Exception as e:
            result = {
                "status": str(e),
                "raw": "",
                "counter": {},
            }

        self.finished.emit(result)


# ================= MAIN WINDOW =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent V2 PRO")
        self.resize(1300, 750)

        self.worker = None

        self.init_ui()
        self.load_data()

    # ================= UI =================
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # ===== SIDEBAR =====
        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("🖨️ Agent V2"))

        sidebar.addWidget(QPushButton("🏠 Tổng quan"))
        sidebar.addWidget(QPushButton("🖨️ Máy"))
        sidebar.addWidget(QPushButton("🏢 Đơn vị"))

        btn_method = QPushButton("⚙️ Method")
        btn_method.clicked.connect(self.open_method)
        sidebar.addWidget(btn_method)

        sidebar.addStretch()

        # ===== CONTENT =====
        content = QVBoxLayout()

        self.header = QLabel("📊 Danh sách máy")
        self.header.setStyleSheet("font-size:20px;font-weight:bold;")
        content.addWidget(self.header)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Code", "Name", "IP",
            "Location", "Serial",
            "Method", "URL", "RAW"
        ])

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        self.table.cellClicked.connect(self.show_detail)
        self.table.itemSelectionChanged.connect(self.on_select)

        content.addWidget(self.table)

        # ===== DETAIL =====
        self.detail = QLabel("Chọn máy để xem chi tiết")
        content.addWidget(self.detail)

        # ===== BUTTON =====
        btn_add = QPushButton("➕ Thêm máy")
        btn_add.clicked.connect(self.add_machine)

        self.btn_edit = QPushButton("✏️ Sửa")
        self.btn_delete = QPushButton("🗑️ Xóa")

        self.btn_edit.clicked.connect(self.edit_machine)
        self.btn_delete.clicked.connect(self.delete_machine)

        btn_fetch = QPushButton("🔄 Lấy Counter")
        btn_fetch.clicked.connect(self.fetch_counter)

        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(btn_fetch)

        content.addLayout(btn_layout)

        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content, 5)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    # ================= LOAD DATA =================
    def load_data(self):
        machines = query("SELECT * FROM machine", fetch=True) or []

        self.table.setRowCount(len(machines))

        for row, machine in enumerate(machines):
            code = machine[2]
            name = machine[3]
            serial = machine[4]
            ip = machine[5]
            url = machine[6]
            location = machine[11] or ""
            method = machine[12] or ""
            raw = machine[13] or ""

            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(ip))
            self.table.setItem(row, 3, QTableWidgetItem(location))
            self.table.setItem(row, 4, QTableWidgetItem(serial))
            self.table.setItem(row, 5, QTableWidgetItem(method))
            self.table.setItem(row, 6, QTableWidgetItem(url))

            btn = QPushButton("Xem")
            btn.clicked.connect(lambda _, r=raw: self.show_raw(r))
            self.table.setCellWidget(row, 7, btn)

        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

    # ================= SELECT =================
    def on_select(self):
        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def get_selected_machine(self):
        row = self.table.currentRow()
        if row == -1:
            return None

        code = self.table.item(row, 0).text()
        data = query(
            "SELECT * FROM machine WHERE machine_code=?",
            (code,),
            fetch=True
        )

        return data[0] if data else None

    # ================= DETAIL =================
    def show_detail(self, row, column):
        code = self.table.item(row, 0).text()
        self.detail.setText(f"🖨️ Máy: {code}")

    # ================= RAW =================
    def show_raw(self, raw):
        dialog = QDialog(self)
        layout = QVBoxLayout()

        text = QTextEdit()
        text.setPlainText(raw or "No data")

        layout.addWidget(text)

        dialog.setLayout(layout)
        dialog.resize(700, 500)
        dialog.exec()

    # ================= METHOD =================
    def open_method(self):
        dialog = MethodWindow()
        dialog.exec()

    # ================= FETCH COUNTER =================
    def fetch_counter(self):
        machine = self.get_selected_machine()

        if not machine:
            QMessageBox.warning(self, "Lỗi", "Chọn máy trước")
            return

        method = query(
            "SELECT * FROM data_method WHERE code=?",
            (machine[12],),
            fetch=True
        )

        if not method:
            QMessageBox.warning(self, "Lỗi", "Không có method")
            return

        self.worker = FetchWorker(machine, method[0])
        self.worker.finished.connect(self.on_fetch_done)
        self.worker.start()

        self.setCursor(Qt.WaitCursor)

    def on_fetch_done(self, result):
        self.setCursor(Qt.ArrowCursor)

        if result["status"] != "OK":
            QMessageBox.warning(self, "Lỗi", result["status"])
            return

        machine = self.get_selected_machine()

        # lưu raw
        query(
            "UPDATE machine SET raw_data=? WHERE id=?",
            (result["raw"], machine[0])
        )

        counter = result["counter"]

        # lưu counter đầy đủ
        query("""
        INSERT INTO counter_log (
            machine_id, timestamp,
            total, bw, color,
            copy, printer, scan, raw
        ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)
        """, (
            machine[0],
            counter.get("total", 0),
            counter.get("bw", 0),
            counter.get("color", 0),
            counter.get("copy", 0),
            counter.get("printer", 0),
            counter.get("scan", 0),
            result.get("raw", "")
        ))

        self.detail.setText(
            f"""
🖨️ Máy: {machine[2]}

📊 Counter:
Total: {counter.get('total', 0)}
BW: {counter.get('bw', 0)}
Color: {counter.get('color', 0)}
Copy: {counter.get('copy', 0)}
Print: {counter.get('printer', 0)}
Scan: {counter.get('scan', 0)}
"""
        )

        QMessageBox.information(self, "OK", "Đã lấy counter")

    # ================= ADD / EDIT / DELETE =================
    def add_machine(self):
        QMessageBox.information(self, "Info", "Chưa triển khai")

    def edit_machine(self):
        QMessageBox.information(self, "Info", "Chưa triển khai")

    def delete_machine(self):
        QMessageBox.information(self, "Info", "Chưa triển khai")