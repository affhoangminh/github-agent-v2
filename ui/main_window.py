from PySide6.QtWidgets import *
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

            res = requests.get(full_url, timeout=5)
            raw = res.text

            parser_name = self.method[5]  # counter_method

            counter = parse_counter(raw, parser_name)

            result = {
                "status": "OK",
                "raw": raw,
                "counter": counter
            }

        except Exception as e:
            result = {
                "status": str(e),
                "raw": "",
                "counter": {}
            }

        self.finished.emit(result)


# ================= MAIN WINDOW =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent V2 PRO")
        self.resize(1300, 750)

        self.init_ui()
        self.load_data()

    # ================= UI =================
    def init_ui(self):
        main = QWidget()
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
            "Method", "URL",
            "RAW"
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

        main.setLayout(main_layout)
        self.setCentralWidget(main)

    # ================= LOAD DATA =================
    def load_data(self):
        machines = query("SELECT * FROM machine", fetch=True)

        self.table.setRowCount(len(machines))

        for i, m in enumerate(machines):
            code = m[2]
            name = m[3]
            serial = m[4]
            ip = m[5]
            url = m[6]
            location = m[11] or ""
            method = m[12] or ""
            raw = m[13] or ""

            self.table.setItem(i, 0, QTableWidgetItem(code))
            self.table.setItem(i, 1, QTableWidgetItem(name))
            self.table.setItem(i, 2, QTableWidgetItem(ip))
            self.table.setItem(i, 3, QTableWidgetItem(location))
            self.table.setItem(i, 4, QTableWidgetItem(serial))
            self.table.setItem(i, 5, QTableWidgetItem(method))
            self.table.setItem(i, 6, QTableWidgetItem(url))

            btn = QPushButton("Xem")
            btn.clicked.connect(lambda _, r=raw: self.show_raw(r))
            self.table.setCellWidget(i, 7, btn)

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
        data = query("SELECT * FROM machine WHERE machine_code=?", (code,), fetch=True)
        return data[0] if data else None

    # ================= DETAIL =================
    def show_detail(self, row, col):
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
        m = self.get_selected_machine()
        if not m:
            QMessageBox.warning(self, "Lỗi", "Chọn máy trước")
            return

        method = query(
            "SELECT * FROM data_method WHERE code=?",
            (m[12],),
            fetch=True
        )

        if not method:
            QMessageBox.warning(self, "Lỗi", "Không có method")
            return

        method = method[0]

        self.worker = FetchWorker(m, method)
        self.worker.finished.connect(self.on_fetch_done)
        self.worker.start()

        self.setCursor(Qt.WaitCursor)

    def on_fetch_done(self, result):
        self.setCursor(Qt.ArrowCursor)

        if result["status"] != "OK":
            QMessageBox.warning(self, "Lỗi", result["status"])
            return

        m = self.get_selected_machine()

        query(
            "UPDATE machine SET raw_data=? WHERE id=?",
            (result["raw"], m[0])
        )

        c = result["counter"]

        query("""
        INSERT INTO counter_log (
            machine_id, timestamp,
            total, bw, color
        ) VALUES (?, datetime('now'), ?, ?, ?)
        """, (
            m[0],
            c.get("total", 0),
            c.get("bw", 0),
            c.get("color", 0)
        ))

        self.detail.setText(f"""
🖨️ Máy: {m[2]}

📊 Counter:
Total: {c.get('total', 0)}
BW: {c.get('bw', 0)}
Color: {c.get('color', 0)}
""")

        QMessageBox.information(self, "OK", "Đã lấy counter")

    # ================= ADD =================
    def add_machine(self):
        dialog = QDialog(self)
        layout = QVBoxLayout()

        code = QLineEdit()
        name = QLineEdit()
        serial = QLineEdit()
        ip = QLineEdit()
        location = QLineEdit()

        method = QComboBox()
        methods = query("SELECT code FROM data_method", fetch=True)
        for m in methods:
            method.addItem(m[0])

        url = QLineEdit()

        layout.addWidget(QLabel("Code"))
        layout.addWidget(code)

        layout.addWidget(QLabel("Name"))
        layout.addWidget(name)

        layout.addWidget(QLabel("Serial"))
        layout.addWidget(serial)

        layout.addWidget(QLabel("IP"))
        layout.addWidget(ip)

        layout.addWidget(QLabel("Location"))
        layout.addWidget(location)

        layout.addWidget(QLabel("Method"))
        layout.addWidget(method)

        layout.addWidget(QLabel("URL"))
        layout.addWidget(url)

        btn = QPushButton("Lưu")

        def save():
            query("""
            INSERT INTO machine (
                org_id, machine_code, name, serial, ip,
                data_url, storage_code, max_days, times_per_day, note,
                location, method_code, raw_data
            ) VALUES (1, ?, ?, ?, ?, ?, 'RICOH', 30, 3, '',
                      ?, ?, '')
            """, (
                code.text(),
                name.text(),
                serial.text(),
                ip.text(),
                url.text(),
                location.text(),
                method.currentText()
            ))

            dialog.accept()
            self.load_data()

        btn.clicked.connect(save)
        layout.addWidget(btn)

        dialog.setLayout(layout)
        dialog.exec()

    # ================= EDIT =================
    def edit_machine(self):
        m = self.get_selected_machine()
        if not m:
            return

        dialog = QDialog(self)
        layout = QVBoxLayout()

        code = QLineEdit(m[2])
        name = QLineEdit(m[3])
        serial = QLineEdit(m[4])
        ip = QLineEdit(m[5])
        location = QLineEdit(m[11] or "")

        method = QComboBox()
        methods = query("SELECT code FROM data_method", fetch=True)
        for mm in methods:
            method.addItem(mm[0])
        method.setCurrentText(m[12] or "")

        url = QLineEdit(m[6] or "")

        layout.addWidget(QLabel("Code"))
        layout.addWidget(code)

        layout.addWidget(QLabel("Name"))
        layout.addWidget(name)

        layout.addWidget(QLabel("Serial"))
        layout.addWidget(serial)

        layout.addWidget(QLabel("IP"))
        layout.addWidget(ip)

        layout.addWidget(QLabel("Location"))
        layout.addWidget(location)

        layout.addWidget(QLabel("Method"))
        layout.addWidget(method)

        layout.addWidget(QLabel("URL"))
        layout.addWidget(url)

        btn = QPushButton("Update")

        def save():
            query("""
            UPDATE machine SET
                machine_code=?, name=?, serial=?, ip=?,
                location=?, method_code=?, data_url=?
            WHERE id=?
            """, (
                code.text(),
                name.text(),
                serial.text(),
                ip.text(),
                location.text(),
                method.currentText(),
                url.text(),
                m[0]
            ))

            dialog.accept()
            self.load_data()

        btn.clicked.connect(save)
        layout.addWidget(btn)

        dialog.setLayout(layout)
        dialog.exec()

    # ================= DELETE =================
    def delete_machine(self):
        m = self.get_selected_machine()
        if not m:
            return

        if QMessageBox.question(self, "Xóa", f"Xóa {m[2]}?") == QMessageBox.Yes:
            query("DELETE FROM machine WHERE id=?", (m[0],))
            self.load_data()