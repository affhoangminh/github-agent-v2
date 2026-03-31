from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal

import requests
import webbrowser

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

            print("\n===== RUN MACHINE =====")
            print("FULL URL:", full_url)

            parser_name = self.method[5]

            if "Toshiba" in parser_name:
                raw = self.fetch_toshiba(full_url)
            else:
                response = requests.get(full_url, timeout=5)
                raw = response.text

            parser_name = self.method[5]
            print("👉 Load parser:", parser_name)

            counter = parse_counter(raw, parser_name)

            print("👉 Parse result:", counter)

            result = {
                "status": "OK",
                "raw": raw,
                "counter": counter,
            }

        except Exception as e:
            print("❌ ERROR:", e)
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

        # 🔥 giữ thread để tránh crash
        self.workers = []

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

        self.header = QLabel("📊 Dashboard máy photocopy")
        self.header.setStyleSheet("font-size:20px;font-weight:bold;")
        content.addWidget(self.header)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Code", "Name", "IP",
            "Status", "Counter",
            "URL", "RAW", "Action"
        ])

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

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

        btn_reload = QPushButton("🔄 Reload")
        btn_reload.clicked.connect(self.load_data)

        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(btn_reload)

        content.addLayout(btn_layout)

        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content, 5)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    # ================= CHECK ONLINE =================
    def check_online(self, ip):
        try:
            requests.get(f"http://{ip}", timeout=2)
            return True
        except:
            return False

    # ================= LOAD DATA =================
    def load_data(self):
        machines = query("SELECT * FROM machine", fetch=True) or []

        self.table.setRowCount(len(machines))

        for row, machine in enumerate(machines):
            code = machine[2]
            name = machine[3]
            ip = machine[5]
            url = machine[6]
            raw = machine[13] or ""

            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(ip))

            # ===== STATUS =====
            online = self.check_online(ip)
            status = "🟢 Online" if online else "🔴 Offline"

            item_status = QTableWidgetItem(status)
            item_status.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, item_status)

            # ===== COUNTER =====
            self.table.setItem(row, 4, QTableWidgetItem("..."))

            # ===== URL BUTTON =====
            full_url = f"http://{ip}{url}"
            btn_url = QPushButton("🌐")
            btn_url.setToolTip(full_url)
            btn_url.clicked.connect(lambda _, u=full_url: self.open_url(u))
            self.table.setCellWidget(row, 5, btn_url)

            # ===== RAW BUTTON =====
            btn_raw = QPushButton("📄")
            btn_raw.clicked.connect(lambda _, r=raw: self.show_raw(r))
            self.table.setCellWidget(row, 6, btn_raw)

            # ===== ACTION BUTTON =====
            btn_fetch = QPushButton("⚡")
            btn_fetch.clicked.connect(lambda _, r=row: self.fetch_row(r))
            self.table.setCellWidget(row, 7, btn_fetch)

            # ===== COLOR OFFLINE =====
            if not online:
                for col in range(5):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(Qt.red)

        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

    # ================= FETCH 1 ROW =================
    def fetch_row(self, row):
        code = self.table.item(row, 0).text()

        machine = query(
            "SELECT * FROM machine WHERE machine_code=?",
            (code,),
            fetch=True
        )[0]

        method = query(
            "SELECT * FROM data_method WHERE code=?",
            (machine[12],),
            fetch=True
        )

        if not method:
            QMessageBox.warning(self, "Lỗi", "Không có method")
            return

        worker = FetchWorker(machine, method[0])

        # 🔥 giữ reference tránh crash
        self.workers.append(worker)

        worker.finished.connect(
            lambda result, r=row, w=worker: self.update_row_safe(result, r, w)
        )

        worker.start()

    # ================= UPDATE SAFE =================
    def update_row_safe(self, result, row, worker):
        code = self.table.item(row, 0).text()

        machine = query(
            "SELECT * FROM machine WHERE machine_code=?",
            (code,),
            fetch=True
        )[0]

        if result["status"] != "OK":
            self.table.setItem(row, 4, QTableWidgetItem("❌ Error"))
        else:
            counter = result["counter"]

            # ===== UPDATE UI =====
            text = f"T:{counter.get('total',0)} | BW:{counter.get('bw',0)}"
            self.table.setItem(row, 4, QTableWidgetItem(text))

            # ===== 🔥 LƯU RAW =====
            query(
                "UPDATE machine SET raw_data=? WHERE id=?",
                (result["raw"], machine[0])
            )

            # ===== 🔥 LƯU COUNTER LOG =====
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

            print("🔥 SAVED TO DB:", counter)

        # ===== cleanup thread =====
        if worker in self.workers:
            self.workers.remove(worker)

        worker.quit()
        worker.wait()

    # ================= OPEN URL =================
    def open_url(self, url):
        webbrowser.open(url)

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

    # ================= fetch_toshiba  =================
    def fetch_toshiba(self, url):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from time import sleep

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=options)

        print("🔥 Selenium loading Toshiba...")

        driver.get(url)

        sleep(5)  # đợi JS load

        html = driver.page_source

        driver.quit()

        return html

    # ================= METHOD =================
    def open_method(self):
        dialog = MethodWindow()
        dialog.exec()

    # ================= CRUD =================
    def add_machine(self):
        QMessageBox.information(self, "Info", "Chưa triển khai")

    def edit_machine(self):
        QMessageBox.information(self, "Info", "Chưa triển khai")

    def delete_machine(self):
        QMessageBox.information(self, "Info", "Chưa triển khai")