from PySide6.QtWidgets import *
from database.db import query


class MethodWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý Method")
        self.resize(900, 500)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Code", "Name", "Path", "Parser", "Counter"
        ])
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        btn_add = QPushButton("➕ Thêm")
        btn_edit = QPushButton("✏️ Sửa")
        btn_delete = QPushButton("🗑️ Xóa")

        btn_add.clicked.connect(self.add_method)
        btn_edit.clicked.connect(self.edit_method)
        btn_delete.clicked.connect(self.delete_method)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # ================= LOAD =================
    def load_data(self):
        data = query("SELECT * FROM danh_muc_method", fetch=True)

        self.table.setRowCount(len(data))

        for i, m in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(m["code_method"]))
            self.table.setItem(i, 1, QTableWidgetItem(m["name_method"]))
            self.table.setItem(i, 2, QTableWidgetItem(m["path_method"]))
            self.table.setItem(i, 3, QTableWidgetItem(m["parser_method"]))
            self.table.setItem(i, 4, QTableWidgetItem(m["counter_method"]))

    def get_selected(self):
        row = self.table.currentRow()
        if row == -1:
            return None

        code = self.table.item(row, 0).text()

        data = query("""
            SELECT * FROM danh_muc_method
            WHERE code_method=?
        """, (code,), fetch=True)

        return data[0] if data else None

    # ================= ADD =================
    def add_method(self):
        dialog = QDialog(self)
        layout = QVBoxLayout()

        code = QLineEdit()
        name = QLineEdit()
        path = QLineEdit()
        parser = QLineEdit()
        counter = QLineEdit()

        layout.addWidget(QLabel("Code"))
        layout.addWidget(code)

        layout.addWidget(QLabel("Name"))
        layout.addWidget(name)

        layout.addWidget(QLabel("Path"))
        layout.addWidget(path)

        layout.addWidget(QLabel("Parser Method"))
        layout.addWidget(parser)

        layout.addWidget(QLabel("Counter Method"))
        layout.addWidget(counter)

        btn = QPushButton("Lưu")

        def save():
            query("""
                INSERT INTO danh_muc_method
                (code_method, name_method, path_method, parser_method, counter_method)
                VALUES (?, ?, ?, ?, ?)
            """, (
                code.text(),
                name.text(),
                path.text(),
                parser.text(),
                counter.text()
            ))

            dialog.accept()
            self.load_data()

        btn.clicked.connect(save)
        layout.addWidget(btn)

        dialog.setLayout(layout)
        dialog.exec()

    # ================= EDIT =================
    def edit_method(self):
        m = self.get_selected()
        if not m:
            return

        dialog = QDialog(self)
        layout = QVBoxLayout()

        code = QLineEdit(m["code_method"])
        name = QLineEdit(m["name_method"])
        path = QLineEdit(m["path_method"])
        parser = QLineEdit(m["parser_method"])
        counter = QLineEdit(m["counter_method"])

        layout.addWidget(QLabel("Code"))
        layout.addWidget(code)

        layout.addWidget(QLabel("Name"))
        layout.addWidget(name)

        layout.addWidget(QLabel("Path"))
        layout.addWidget(path)

        layout.addWidget(QLabel("Parser"))
        layout.addWidget(parser)

        layout.addWidget(QLabel("Counter"))
        layout.addWidget(counter)

        btn = QPushButton("Cập nhật")

        def save():
            query("""
                UPDATE danh_muc_method
                SET code_method=?, name_method=?, path_method=?,
                    parser_method=?, counter_method=?
                WHERE code_method=?
            """, (
                code.text(),
                name.text(),
                path.text(),
                parser.text(),
                counter.text(),
                m["code_method"]
            ))

            dialog.accept()
            self.load_data()

        btn.clicked.connect(save)
        layout.addWidget(btn)

        dialog.setLayout(layout)
        dialog.exec()

    # ================= DELETE =================
    def delete_method(self):
        m = self.get_selected()
        if not m:
            return

        query("""
            DELETE FROM danh_muc_method
            WHERE code_method=?
        """, (m["code_method"],))

        self.load_data()