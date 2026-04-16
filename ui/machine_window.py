from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QCheckBox, QLabel, QGroupBox,
    QFormLayout, QGridLayout, QMessageBox, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from database.db import query

class MachineWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Quản Lý Danh Sách Máy Photocopy")
        self.resize(1100, 700)
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
                gridline-color: #f0f0f0;
            }
            QTableWidget::item { padding: 5px; }
            QHeaderView::section {
                background-color: #e9edf5;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
                color: #2b3a8a;
            }
            QPushButton#actionBtn {
                background-color: #2b3a8a;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton#deleteBtn {
                background-color: #c0392b;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover { opacity: 0.9; }
        """)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        title_label = QLabel("📋 DANH SÁCH THIẾT BỊ")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2b3a8a;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.btn_refresh = QPushButton("🔄 Làm mới")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_close = QPushButton("Đóng")
        self.btn_close.setFixedWidth(100)
        self.btn_close.clicked.connect(self.reject)
        
        header_layout.addWidget(self.btn_refresh)
        header_layout.addWidget(self.btn_close)
        
        layout.addLayout(header_layout)

        # --- TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Mã Máy", "Tên Thiết Bị", "Địa Chỉ IP", 
            "Dòng Máy (Method)", "Vị Trí Đặt Máy", "Trạng Thái"
        ])
        
        # Tự động co giãn các cột
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)

        # --- ACTION BUTTONS ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_add = QPushButton("➕ THÊM MÁY MỚI")
        self.btn_add.setObjectName("actionBtn")
        self.btn_add.clicked.connect(self.add_machine)

        self.btn_edit = QPushButton("✏️ SỬA THÔNG TIN")
        self.btn_edit.setObjectName("actionBtn")
        self.btn_edit.clicked.connect(self.edit_machine)

        self.btn_delete = QPushButton("🗑️ XÓA THIẾT BỊ")
        self.btn_delete.setObjectName("deleteBtn")
        self.btn_delete.clicked.connect(self.delete_machine)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_delete)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_data(self):
        data = query("SELECT * FROM machine", fetch=True)
        self.table.setRowCount(len(data))

        for i, m in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(m["code_machine"]))
            self.table.setItem(i, 1, QTableWidgetItem(m["name_machine"]))
            
            ip_item = QTableWidgetItem(m["ip_machine"])
            ip_item.setForeground(Qt.blue)
            self.table.setItem(i, 2, ip_item)
            
            self.table.setItem(i, 3, QTableWidgetItem(m["code_method"]))
            self.table.setItem(i, 4, QTableWidgetItem(m["location"] or ""))
            
            status = "✅ Đang chạy" if m["counter_enabled"] else "❌ Tắt"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, status_item)

    def get_selected_code(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một dòng trên bảng!")
            return None
        return self.table.item(row, 0).text()

    def add_machine(self):
        dlg = MachineEditDialog(parent=self)
        if dlg.exec():
            self.load_data()

    def edit_machine(self):
        code = self.get_selected_code()
        if not code: return
        
        data = query("SELECT * FROM machine WHERE code_machine=?", (code,), fetch=True)
        if data:
            dlg = MachineEditDialog(data[0], parent=self)
            if dlg.exec():
                self.load_data()

    def delete_machine(self):
        code = self.get_selected_code()
        if not code: return
        
        reply = QMessageBox.question(
            self, "Xác nhận", f"Bạn có chắc muốn xóa máy {code}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            query("DELETE FROM machine WHERE code_machine=?", (code,))
            self.load_data()


class MachineEditDialog(QDialog):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("📜 Chi Tiết Máy Photocopy" if data else "➕ Thêm Máy Photocopy Mới")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        self.setStyleSheet("""
            QDialog { background-color: #f9f9f9; }
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #dcdcdc; 
                border-radius: 8px; 
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #2b3a8a; }
            QLineEdit, QComboBox { 
                border: 1px solid #ccc; 
                border-radius: 4px; 
                padding: 6px; 
                background: white;
            }
            QLineEdit:focus { border: 1px solid #2b3a8a; background: #f0f4ff; }
        """)

        # --- THÔNG TIN THIẾT BỊ ---
        group_info = QGroupBox("🏗️ Thông Tin Thiết Bị")
        form_info = QFormLayout()
        
        # Lưu mã cũ để dùng trong mệnh đề WHERE khi UPDATE
        self.old_code = self.data["code_machine"] if self.data else None
        
        self.txt_code = QLineEdit(self.data["code_machine"] if self.data else "")
        self.txt_name = QLineEdit(self.data["name_machine"] if self.data else "")
        self.txt_serial = QLineEdit(self.data["serial_machine"] if self.data else "")
        self.txt_location = QLineEdit(self.data["location"] if self.data else "")
        
        form_info.addRow("Mã Máy (Duy nhất):", self.txt_code)
        form_info.addRow("Tên Thiết Bị:", self.txt_name)
        form_info.addRow("Số Serial:", self.txt_serial)
        form_info.addRow("Vị Trí Đặt Máy:", self.txt_location)
        group_info.setLayout(form_info)
        layout.addWidget(group_info)

        # --- CẤU HÌNH KẾT NỐI ---
        group_net = QGroupBox("🌐 Cấu Hình Kết Nối IP")
        form_net = QGridLayout()

        self.txt_ip = QLineEdit(self.data["ip_machine"] if self.data else "")
        self.cb_method = QComboBox()
        methods = query("SELECT code_method FROM danh_muc_method", fetch=True)
        for m in methods: self.cb_method.addItem(m["code_method"])
        
        if self.data:
            idx = self.cb_method.findText(self.data["code_method"])
            if idx >= 0: self.cb_method.setCurrentIndex(idx)

        self.txt_path = QLineEdit(self.data["path_machine"] if self.data else "")
        self.txt_path.setStyleSheet("background-color: #ffffff; color: #333;")

        form_net.addWidget(QLabel("Địa Chỉ IP:"), 0, 0)
        form_net.addWidget(self.txt_ip, 0, 1)
        form_net.addWidget(QLabel("Dòng Máy (Parser):"), 1, 0)
        form_net.addWidget(self.cb_method, 1, 1)
        form_net.addWidget(QLabel("Đường Dẫn Log (Path):"), 2, 0)
        form_net.addWidget(self.txt_path, 2, 1)
        
        # Link method change
        self.cb_method.currentTextChanged.connect(self.update_path)
        if not self.data: self.update_path() # Initial path for new machine

        group_net.setLayout(form_net)
        layout.addWidget(group_net)

        # --- CHỈ SỐ VẬN HÀNH ---
        group_ops = QGroupBox("⚙️ Chỉ Số Vận Hành")
        form_ops = QHBoxLayout()

        self.cb_enabled = QCheckBox("Kích hoạt lấy Counter tự động")
        if self.data: self.cb_enabled.setChecked(bool(self.data["counter_enabled"]))
        else: self.cb_enabled.setChecked(True)

        form_ops.addStretch()
        form_ops.addWidget(self.cb_enabled)

        group_ops.setLayout(form_ops)
        layout.addWidget(group_ops)

        # --- BUTTONS ---
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 LƯU DỮ LIỆU")
        self.btn_save.setMinimumHeight(45)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2b3a8a;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #3d4fb3; }
        """)
        self.btn_save.clicked.connect(self.save)
        
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setMinimumHeight(45)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_path(self):
        method_code = self.cb_method.currentText()
        if not method_code: return
        res = query("SELECT path_method FROM danh_muc_method WHERE code_method=?", (method_code,), fetch=True)
        if res: self.txt_path.setText(res[0]["path_method"])

    def save(self):
        # Validate simple
        if not self.txt_code.text() or not self.txt_ip.text():
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập đầy đủ Mã Máy và IP!")
            return

        # Lấy mã đơn vị mặc định
        res_dv = query("SELECT code_don_vi FROM danh_muc_don_vi WHERE id_donvi=1", fetch=True)
        code_don_vi = res_dv[0]["code_don_vi"] if res_dv else "DV001"

        vals = (
            self.txt_code.text(), self.txt_name.text(), self.txt_serial.text(),
            self.txt_ip.text(), self.txt_path.text(), self.txt_location.text(),
            self.cb_method.currentText(), 1 if self.cb_enabled.isChecked() else 0,
            code_don_vi
        )

        if self.data:
            query("""
                UPDATE machine SET
                    code_machine=?, name_machine=?, serial_machine=?,
                    ip_machine=?, path_machine=?, location=?,
                    code_method=?, 
                    counter_enabled=?, code_don_vi=?
                WHERE code_machine=?
            """, (*vals, self.old_code))
        else:
            # Check duplicate code
            check = query("SELECT code_machine FROM machine WHERE code_machine=?", (vals[0],), fetch=True)
            if check:
                QMessageBox.critical(self, "Lỗi", "Mã máy này đã tồn tại!")
                return
            query("""
                INSERT INTO machine (
                    code_machine, name_machine, serial_machine,
                    ip_machine, path_machine, location,
                    code_method, 
                    counter_enabled, code_don_vi
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, vals)

        self.accept()