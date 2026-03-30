from PySide6.QtWidgets import *
from database.db import query


class MethodWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý Method")
        self.resize(800, 500)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # TABLE
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Code", "Name", "URL", "Parser", "Counter"
        ])
        layout.addWidget(self.table)

        # BUTTON
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
        data = query("SELECT * FROM data_method", fetch=True)

        self.table.setRowCount(len(data))

        for i, m in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(m[1]))
            self.table.setItem(i, 1, QTableWidgetItem(m[2]))
            self.table.setItem(i, 2, QTableWidgetItem(m[3]))
            self.table.setItem(i, 3, QTableWidgetItem(m[4]))
            self.table.setItem(i, 4, QTableWidgetItem(m[5]))

    def get_selected(self):
        row = self.table.currentRow()
        if row == -1:
            return None

        code = self.table.item(row, 0).text()
        data = query("SELECT * FROM data_method WHERE code=?", (code,), fetch=True)
        return data[0] if data else None

    # ================= ADD =================
    def add_method(self):
        dialog = QDialog(self)
        layout = QVBoxLayout()

        code = QLineEdit()
        name = QLineEdit()
        url = QLineEdit()
        parser = QLineEdit()
        counter = QLineEdit()

        layout.addWidget(QLabel("Code"))
        layout.addWidget(code)

        layout.addWidget(QLabel("Name"))
        layout.addWidget(name)

        layout.addWidget(QLabel("URL"))
        layout.addWidget(url)

        layout.addWidget(QLabel("Parser Method"))
        layout.addWidget(parser)

        layout.addWidget(QLabel("Counter Method"))
        layout.addWidget(counter)

        btn = QPushButton("Lưu")

        def save():
            query("""
            INSERT INTO data_method (code, name, data_url, parser_method, counter_method)
            VALUES (?, ?, ?, ?, ?)
            """, (
                code.text(),
                name.text(),
                url.text(),
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

        code = QLineEdit(m[1])
        name = QLineEdit(m[2])
        url = QLineEdit(m[3])
        parser = QLineEdit(m[4])
        counter = QLineEdit(m[5])

        layout.addWidget(QLabel("Code"))
        layout.addWidget(code)

        layout.addWidget(QLabel("Name"))
        layout.addWidget(name)

        layout.addWidget(QLabel("URL"))
        layout.addWidget(url)

        layout.addWidget(QLabel("Parser"))
        layout.addWidget(parser)

        layout.addWidget(QLabel("Counter"))
        layout.addWidget(counter)

        btn = QPushButton("Cập nhật")

        def save():
            query("""
            UPDATE data_method
            SET code=?, name=?, data_url=?, parser_method=?, counter_method=?
            WHERE id=?
            """, (
                code.text(),
                name.text(),
                url.text(),
                parser.text(),
                counter.text(),
                m[0]
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

        query("DELETE FROM data_method WHERE id=?", (m[0],))
        self.load_data()