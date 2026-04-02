from PySide6.QtWidgets import *
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

            parser_name = self.method[5]

            # ===== SWITCH FETCH =====
            if "Toshiba" in parser_name:
                raw = self.fetch_toshiba(full_url)
            else:
                res = requests.get(full_url, timeout=5)
                raw = res.text

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

    # ===== SELENIUM =====
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

        sleep(5)

        html = driver.page_source
        driver.quit()

        return html


# ================= MAIN =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent V2 PRO")
        self.resize(1300, 750)

        self.workers = []

        self.init_ui()
        self.load_data()

    # ================= UI =================
    def init_ui(self):
        main = QWidget()
        main_layout = QHBoxLayout()

        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("🖨️ Agent V2"))

        sidebar.addWidget(QPushButton("🏠 Tổng quan"))
        sidebar.addWidget(QPushButton("🖨️ Máy"))
        sidebar.addWidget(QPushButton("🏢 Đơn vị"))

        btn_method = QPushButton("⚙️ Method")
        btn_method.clicked.connect(self.open_method)
        sidebar.addWidget(btn_method)

        sidebar.addStretch()

        content = QVBoxLayout()

        self.header = QLabel("📊 Dashboard máy")
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
        self.table.itemSelectionChanged.connect(self.on_select)

        content.addWidget(self.table)

        self.detail = QLabel("Chọn máy")
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

        main.setLayout(main_layout)
        self.setCentralWidget(main)

    # ================= LOAD =================
    def load_data(self):
        machines = query("SELECT * FROM machine", fetch=True) or []
        self.table.setRowCount(len(machines))

        for row, m in enumerate(machines):
            code = m[2]
            name = m[3]
            ip = m[5]
            url = m[6]
            raw = m[13] or ""

            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(ip))

            # STATUS
            status = "🟢 Online" if self.check_online(ip) else "🔴 Offline"
            self.table.setItem(row, 3, QTableWidgetItem(status))

            self.table.setItem(row, 4, QTableWidgetItem("..."))

            # URL
            full_url = f"http://{ip}{url}"
            btn_url = QPushButton("🌐")
            btn_url.clicked.connect(lambda _, u=full_url: self.open_url(u))
            self.table.setCellWidget(row, 5, btn_url)

            # RAW
            btn_raw = QPushButton("📄")
            btn_raw.clicked.connect(lambda _, r=raw: self.show_raw(r))
            self.table.setCellWidget(row, 6, btn_raw)

            # ACTION
            btn_fetch = QPushButton("⚡")
            btn_fetch.clicked.connect(lambda _, r=row: self.fetch_row(r))
            self.table.setCellWidget(row, 7, btn_fetch)

        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

    # ================= FETCH =================
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
        )[0]

        worker = FetchWorker(machine, method)
        self.workers.append(worker)

        worker.finished.connect(
            lambda result, r=row, w=worker: self.update_row(result, r, w)
        )

        worker.start()

    def update_row(self, result, row, worker):
        code = self.table.item(row, 0).text()

        machine = query(
            "SELECT * FROM machine WHERE machine_code=?",
            (code,),
            fetch=True
        )[0]

        if result["status"] != "OK":
            self.table.setItem(row, 4, QTableWidgetItem("❌ Error"))
        else:
            c = result["counter"]

            text = f"T:{c.get('total',0)} | BW:{c.get('bw',0)}"
            self.table.setItem(row, 4, QTableWidgetItem(text))

            # SAVE DB
            query(
                "UPDATE machine SET raw_data=? WHERE id=?",
                (result["raw"], machine[0])
            )

            query("""
            INSERT INTO counter_log (
                machine_id, timestamp,
                total, bw, color,
                copy, printer, scan, raw
            ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)
            """, (
                machine[0],
                c.get("total", 0),
                c.get("bw", 0),
                c.get("color", 0),
                c.get("copy", 0),
                c.get("printer", 0),
                c.get("scan", 0),
                result["raw"]
            ))

        if worker in self.workers:
            self.workers.remove(worker)

        worker.quit()
        worker.wait()

    # ================= UTIL =================
    def check_online(self, ip):
        try:
            requests.get(f"http://{ip}", timeout=2)
            return True
        except:
            return False

    def open_url(self, url):
        webbrowser.open(url)

    def show_raw(self, raw):
        dialog = QDialog(self)
        layout = QVBoxLayout()

        text = QTextEdit()
        text.setPlainText(raw or "No data")

        layout.addWidget(text)

        dialog.setLayout(layout)
        dialog.resize(700, 500)
        dialog.exec()

    def open_method(self):
        dialog = MethodWindow()
        dialog.exec()

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

    # ================= CRUD =================
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

        for label, widget in [
            ("Code", code), ("Name", name), ("Serial", serial),
            ("IP", ip), ("Location", location),
            ("Method", method), ("URL", url)
        ]:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

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

        for label, widget in [
            ("Code", code), ("Name", name), ("Serial", serial),
            ("IP", ip), ("Location", location),
            ("Method", method), ("URL", url)
        ]:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

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

    def delete_machine(self):
        m = self.get_selected_machine()
        if not m:
            return

        if QMessageBox.question(self, "Xóa", f"Xóa {m[2]}?") == QMessageBox.Yes:
            query("DELETE FROM machine WHERE id=?", (m[0],))
            self.load_data()