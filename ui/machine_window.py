from PySide6.QtWidgets import *
from database.db import query


class MachineWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quản lý Máy")
        self.resize(1200, 650)

        self.init_ui()
        self.load_data()

    # ================= UI =================
    def init_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Mã", "Tên", "Serial", "IP",
            "Path", "Method", "Vị trí",
            "Số ngày", "Lần/ngày", "ON/OFF"
        ])
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        btn_add = QPushButton("➕ Thêm")
        btn_edit = QPushButton("✏️ Sửa")
        btn_delete = QPushButton("🗑️ Xóa")

        btn_add.clicked.connect(self.add_machine)
        btn_edit.clicked.connect(self.edit_machine)
        btn_delete.clicked.connect(self.delete_machine)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # ================= LOAD =================
    def load_data(self):
        data = query("SELECT * FROM machine", fetch=True)

        self.table.setRowCount(len(data))

        for i, m in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(m["code_machine"]))
            self.table.setItem(i, 1, QTableWidgetItem(m["name_machine"]))
            self.table.setItem(i, 2, QTableWidgetItem(m["serial_machine"] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(m["ip_machine"]))
            self.table.setItem(i, 4, QTableWidgetItem(m["path_machine"]))
            self.table.setItem(i, 5, QTableWidgetItem(m["code_method"]))
            self.table.setItem(i, 6, QTableWidgetItem(m["location"] or ""))
            self.table.setItem(i, 7, QTableWidgetItem(str(m["max_days"])))
            self.table.setItem(i, 8, QTableWidgetItem(str(m["times_per_day"])))
            self.table.setItem(i, 9, QTableWidgetItem("ON" if m["counter_enabled"] else "OFF"))

    def get_selected(self):
        row = self.table.currentRow()
        if row == -1:
            return None

        code = self.table.item(row, 0).text()
        data = query("SELECT * FROM machine WHERE code_machine=?", (code,), fetch=True)
        return data[0] if data else None

    # ================= GET PATH =================
    def get_path_by_method(self, code_method):
        data = query("""
            SELECT path_method FROM danh_muc_method
            WHERE code_method=?
        """, (code_method,), fetch=True)

        return data[0]["path_method"] if data else ""

    # ================= GET DON VI =================
    def get_default_donvi(self):
        data = query("""
            SELECT code_don_vi FROM danh_muc_don_vi
            WHERE id_donvi=1
        """, fetch=True)

        return data[0]["code_don_vi"] if data else ""

    # ================= FORM =================
    def open_form(self, data=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Thông tin Máy")
        dialog.resize(900, 550)

        layout = QGridLayout()

        # ===== INPUT =====
        txt_code = QLineEdit(data["code_machine"] if data else "")
        txt_name = QLineEdit(data["name_machine"] if data else "")
        txt_serial = QLineEdit(data["serial_machine"] if data else "")
        txt_ip = QLineEdit(data["ip_machine"] if data else "")
        txt_location = QLineEdit(data["location"] if data else "")
        txt_note = QLineEdit(data["note"] if data else "")
        txt_max_days = QLineEdit(str(data["max_days"]) if data else "30")
        txt_times = QLineEdit(str(data["times_per_day"]) if data else "1")

        if data:
            txt_code.setReadOnly(True)

        # ===== PATH (READONLY) =====
        txt_path = QLineEdit(data["path_machine"] if data else "")
        txt_path.setReadOnly(True)

        # ===== METHOD DROPDOWN =====
        cb_method = QComboBox()
        methods = query("SELECT code_method FROM danh_muc_method", fetch=True)

        for m in methods:
            cb_method.addItem(m["code_method"])

        if data:
            index = cb_method.findText(data["code_method"])
            if index >= 0:
                cb_method.setCurrentIndex(index)

        # ===== AUTO UPDATE PATH =====
        def on_method_change():
            method_code = cb_method.currentText()
            txt_path.setText(self.get_path_by_method(method_code))

        cb_method.currentTextChanged.connect(on_method_change)

        # ===== CHECKBOX =====
        cb_enabled = QCheckBox("Bật lấy counter")
        if data and data["counter_enabled"]:
            cb_enabled.setChecked(True)

        # ===== FIELD LIST =====
        fields = [
            ("Mã Máy", txt_code),
            ("Tên Máy", txt_name),
            ("Serial Máy", txt_serial),
            ("IP", txt_ip),
            ("Path", txt_path),
            ("Method", cb_method),
            ("Vị Trí", txt_location),
            ("Ghi Chú", txt_note),
            ("Số Ngày", txt_max_days),
            ("Lần/ngày", txt_times),
            ("Lấy Counter", cb_enabled),
        ]

        # ===== 2 COLUMN LAYOUT =====
        for i, (label, widget) in enumerate(fields):
            row = i % 6
            col = (i // 6) * 2

            layout.addWidget(QLabel(label), row, col)
            layout.addWidget(widget, row, col + 1)

        # ===== SAVE =====
        btn_save = QPushButton("💾 Lưu")

        def save():
            method_code = cb_method.currentText()
            path = self.get_path_by_method(method_code)
            code_don_vi = self.get_default_donvi()

            values = (
                txt_code.text(),
                txt_name.text(),
                txt_serial.text(),
                txt_ip.text(),
                path,
                txt_location.text(),
                method_code,
                txt_note.text(),
                int(txt_max_days.text()),
                int(txt_times.text()),
                1 if cb_enabled.isChecked() else 0,
                code_don_vi
            )

            if data:
                query("""
                    UPDATE machine SET
                        code_machine=?, name_machine=?, serial_machine=?,
                        ip_machine=?, path_machine=?, location=?,
                        code_method=?, note=?,
                        max_days=?, times_per_day=?, counter_enabled=?,
                        code_don_vi=?
                    WHERE code_machine=?
                """, (*values, data["code_machine"]))
            else:
                query("""
                    INSERT INTO machine (
                        code_machine, name_machine, serial_machine,
                        ip_machine, path_machine, location,
                        code_method, note,
                        max_days, times_per_day, counter_enabled,
                        code_don_vi
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)

            dialog.accept()
            self.load_data()

        btn_save.clicked.connect(save)
        layout.addWidget(btn_save, 7, 3)

        dialog.setLayout(layout)
        dialog.exec()

    # ================= ACTION =================
    def add_machine(self):
        self.open_form()

    def edit_machine(self):
        data = self.get_selected()
        if data:
            self.open_form(data)

    def delete_machine(self):
        data = self.get_selected()
        if not data:
            return

        query("DELETE FROM machine WHERE code_machine=?", (data["code_machine"],))
        self.load_data()