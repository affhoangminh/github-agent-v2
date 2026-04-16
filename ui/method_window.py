import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QGroupBox,
    QFormLayout, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.db import query

class MethodWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quản Lý Phương Thức Kết Nối (Methods)")
        self.resize(1000, 600)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        # Master layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Style chung cho QDialog
        self.setStyleSheet("""
            QDialog { background-color: #f5f6fa; }
            QTableWidget { 
                background-color: white; 
                border: 1px solid #dcdcdc; 
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #e9edf5;
                padding: 8px;
                font-weight: bold;
                color: #2b3a8a;
            }
            QPushButton#actionBtn {
                background-color: #2b3a8a;
                color: white;
                font-weight: bold;
                padding: 8px 18px;
                border-radius: 5px;
            }
            QPushButton#deleteBtn {
                background-color: #c0392b;
                color: white;
                font-weight: bold;
                padding: 8px 18px;
                border-radius: 5px;
            }
        """)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        title_label = QLabel("🛠️ CẤU HÌNH DÒNG MÁY (METHODS)")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2b3a8a;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.btn_close = QPushButton("Đóng")
        self.btn_close.setFixedWidth(100)
        self.btn_close.clicked.connect(self.reject)
        header_layout.addWidget(self.btn_close)
        
        layout.addLayout(header_layout)

        # --- TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Mã Định Danh", "Tên Dòng Máy", "Đường Dẫn Mặc Định (Path)", 
            "Engine (Parser)", "File Xử Lý (Counter)"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)

        # --- ACTION BUTTONS ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_add = QPushButton("➕ Thêm Mới")
        self.btn_add.setObjectName("actionBtn")
        self.btn_add.clicked.connect(self.add_method)

        self.btn_edit = QPushButton("✏️ Chỉnh Sửa")
        self.btn_edit.setObjectName("actionBtn")
        self.btn_edit.clicked.connect(self.edit_method)

        self.btn_delete = QPushButton("🗑️ Xóa")
        self.btn_delete.setObjectName("deleteBtn")
        self.btn_delete.clicked.connect(self.delete_method)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_delete)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_data(self):
        data = query("SELECT * FROM danh_muc_method", fetch=True)
        self.table.setRowCount(len(data))
        for i, m in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(m["code_method"]))
            self.table.setItem(i, 1, QTableWidgetItem(m["name_method"]))
            self.table.setItem(i, 2, QTableWidgetItem(m["path_method"]))
            
            p_item = QTableWidgetItem(m["parser_method"])
            p_item.setForeground(Qt.darkBlue if m["parser_method"] == "requests" else Qt.darkGreen)
            self.table.setItem(i, 3, p_item)
            
            self.table.setItem(i, 4, QTableWidgetItem(m["counter_method"]))

    def get_selected_code(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một hàng trên bảng!")
            return None
        return self.table.item(row, 0).text()

    def add_method(self):
        dlg = MethodEditDialog(parent=self)
        if dlg.exec(): self.load_data()

    def edit_method(self):
        code = self.get_selected_code()
        if not code: return
        data = query("SELECT * FROM danh_muc_method WHERE code_method=?", (code,), fetch=True)
        if data:
            dlg = MethodEditDialog(data[0], parent=self)
            if dlg.exec(): self.load_data()

    def delete_method(self):
        code = self.get_selected_code()
        if not code: return
        reply = QMessageBox.question(self, "Xác nhận", f"Xóa phương thức {code}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            query("DELETE FROM danh_muc_method WHERE code_method=?", (code,))
            self.load_data()

class MethodEditDialog(QDialog):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("📜 Chi Tiết Phương Thức" if data else "➕ Thêm Phương Thức Mới")
        self.resize(600, 450)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        self.setStyleSheet("""
            QLineEdit, QComboBox { 
                padding: 8px; border: 1px solid #ccc; border-radius: 4px; background: white;
            }
            QLineEdit:focus { border: 1px solid #2b3a8a; }
            QLabel { font-weight: bold; color: #555; }
        """)

        form = QFormLayout()
        form.setSpacing(10)
        
        self.old_code = self.data["code_method"] if self.data else None
        self.txt_code = QLineEdit(self.data["code_method"] if self.data else "")
        self.txt_name = QLineEdit(self.data["name_method"] if self.data else "")
        self.txt_path = QLineEdit(self.data["path_method"] if self.data else "")
        
        # Engine dropdown (Tự động quét core/engines)
        self.cb_parser = QComboBox()
        self.cb_parser.setEditable(True)
        engine_dir = os.path.join(os.getcwd(), "core", "engines")
        if os.path.exists(engine_dir):
            engines = [f.replace(".py", "") for f in os.listdir(engine_dir) if f.endswith(".py") and f != "__init__.py"]
            self.cb_parser.addItems(engines)

        if self.data: self.cb_parser.setCurrentText(self.data["parser_method"])
        
        # Tự động quét các file parser trong thư mục core/parsers
        self.cb_counter = QComboBox()
        self.cb_counter.setEditable(True) # Cho phép gõ tên mới
        self.cb_counter.setInsertPolicy(QComboBox.NoInsert) # Không tự động add vào list permanent
        
        parser_dir = os.path.join(os.getcwd(), "core", "parsers")
        if os.path.exists(parser_dir):
            files = [f.replace(".py", "") for f in os.listdir(parser_dir) if f.endswith(".py") and f != "__init__.py"]
            self.cb_counter.addItems(files)
        
        if self.data:
            idx = self.cb_counter.findText(self.data["counter_method"])
            if idx >= 0: self.cb_counter.setCurrentIndex(idx)

        form.addRow("Mã định danh (Code):", self.txt_code)
        form.addRow("Tên dòng máy:", self.txt_name)
        form.addRow("Đường dẫn Log (Path):", self.txt_path)
        form.addRow("Engine xử lý:", self.cb_parser)
        form.addRow("File Parser (trong core/parsers/):", self.cb_counter)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 LƯU")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setStyleSheet("background-color: #2b3a8a; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_save.clicked.connect(self.save)
        
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def save(self):
        if not self.txt_code.text() or not self.txt_name.text():
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập đầy đủ Mã và Tên!")
            return

        vals = (
            self.txt_code.text(), self.txt_name.text(), self.txt_path.text(),
            self.cb_parser.currentText(), self.cb_counter.currentText()
        )

        if self.data:
            query("""
                UPDATE danh_muc_method SET
                    code_method=?, name_method=?, path_method=?,
                    parser_method=?, counter_method=?
                WHERE code_method=?
            """, (*vals, self.old_code))
        else:
            query("""
                INSERT INTO danh_muc_method (code_method, name_method, path_method, parser_method, counter_method)
                VALUES (?, ?, ?, ?, ?)
            """, vals)

        self.accept()