"""
Data Section - PyQt6 Version
Place in: tools/pdf_generator/data_section_pyqt6.py

Manages CSV data with:
- Add/Edit rows manually
- Upload CSV file
- Download empty schema CSV
- Export data to CSV
- Generate PDFs from data
"""
import csv
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDialog, QLineEdit, QFormLayout, QFileDialog, QMessageBox,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap


class RowDialog(QDialog):
    """Dialog for adding/editing a data row"""
    
    def __init__(self, data_nodes, row_data=None, parent=None):
        super().__init__(parent)
        self.data_nodes = data_nodes
        self.row_data = row_data or {}
        self.inputs = {}
        
        self.setWindowTitle("Add New Row" if not row_data else "Edit Row")
        self.setModal(True)
        self.setMinimumWidth(520)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title = QLabel(self.windowTitle())
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        for node in self.data_nodes:
            label = QLabel(f"{node}:")
            label.setStyleSheet("color: #e0e0e0; font-weight: 600; min-width: 140px;")
            
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Enter {node} value...")
            input_field.setText(self.row_data.get(node, ""))
            input_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px 12px;
                    background: #2a2a2a;
                    border: 1px solid #404040;
                    border-radius: 6px;
                    color: white;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border: 1px solid #3b82f6;
                    background: #2f2f2f;
                }
            """)
            
            form_layout.addRow(label, input_field)
            self.inputs[node] = input_field
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #b0b0b0;
                border: 1px solid #505050;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #383838;
                color: white;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save" if self.row_data else "Add Row")
        save_btn.setFixedWidth(100)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def get_data(self):
        return {node: self.inputs[node].text().strip() for node in self.data_nodes}


class DataSectionPyQt6(QWidget):
    """Data section for managing CSV data"""
    
    backRequested = pyqtSignal()
    generatePDFRequested = pyqtSignal()
    
    def __init__(self, project, pdf_data_manager, parent=None):
        super().__init__(parent)
        self.project = project
        self.pdf_data_manager = pdf_data_manager
        
        config = self.pdf_data_manager.load_project_config(self.project["id"])
        self.data_nodes = config.get("data_nodes", [])
        self.fields = config.get("fields", [])
        
        self.csv_data = self.pdf_data_manager.load_csv_data(self.project["id"])
        
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background: #1f1f1f; border-bottom: 1px solid #333;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 18, 30, 18)
        
        title = QLabel(f"Data Table — {self.project['name']}")
        title.setStyleSheet("font-size: 19px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        back_btn = QPushButton("Back to Design")
        back_btn.setFixedHeight(36)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #374151;
                color: white;
                border: none;
                padding: 0 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #4b5563;
            }
        """)
        back_btn.clicked.connect(lambda: self.backRequested.emit())
        header_layout.addWidget(back_btn)
        
        layout.addWidget(header)
        
        # Toolbar with groups
        toolbar = QFrame()
        toolbar.setStyleSheet("background: #171717; border-bottom: 1px solid #2a2a2a;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(30, 14, 30, 14)
        toolbar_layout.setSpacing(24)
        
        info = QLabel(f"Fields: {', '.join(self.data_nodes) if self.data_nodes else 'Not defined'}")
        info.setStyleSheet("color: #9ca3af; font-size: 13px;")
        toolbar_layout.addWidget(info)
        
        toolbar_layout.addStretch()
        
        # Group 1: File operations
        file_group = QFrame()
        file_group.setStyleSheet("""
            QFrame {
                background: #222;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        file_layout = QHBoxLayout(file_group)
        file_layout.setContentsMargins(8, 6, 8, 6)
        file_layout.setSpacing(6)
        
        schema_btn = QPushButton("Download Template")
        schema_btn.setStyleSheet(self._btn_style("#10b981", "#059669"))
        schema_btn.clicked.connect(self.download_schema)
        
        upload_btn = QPushButton("Upload CSV")
        upload_btn.setStyleSheet(self._btn_style("#3b82f6", "#2563eb"))
        upload_btn.clicked.connect(self.upload_csv)
        
        export_btn = QPushButton("Export CSV")
        export_btn.setStyleSheet(self._btn_style("#8b5cf6", "#7c3aed"))
        export_btn.clicked.connect(self.export_csv)
        
        file_layout.addWidget(schema_btn)
        file_layout.addWidget(upload_btn)
        file_layout.addWidget(export_btn)
        toolbar_layout.addWidget(file_group)
        
        # Group 2: Row & PDF actions
        action_group = QFrame()
        action_group.setStyleSheet("""
            QFrame {
                background: #222;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        action_layout = QHBoxLayout(action_group)
        action_layout.setContentsMargins(8, 6, 8, 6)
        action_layout.setSpacing(6)
        
        add_btn = QPushButton("Add Row")
        add_btn.setStyleSheet(self._btn_style("#3b82f6", "#2563eb"))
        add_btn.clicked.connect(self.add_row)
        
        pdf_btn = QPushButton("Generate PDFs")
        pdf_btn.setStyleSheet(self._btn_style("#ef4444", "#dc2626"))
        pdf_btn.clicked.connect(lambda: self.generatePDFRequested.emit())
        
        action_layout.addWidget(add_btn)
        action_layout.addWidget(pdf_btn)
        toolbar_layout.addWidget(action_group)
        
        layout.addWidget(toolbar)
        
        # Table area
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(30, 20, 30, 20)
        
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1a1a1a;
                border: 1px solid #2d2d2d;
                border-radius: 8px;
                color: #e5e7eb;
                gridline-color: #252525;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #1e40af;
            }
            QHeaderView::section {
                background: #222;
                color: #e5e7eb;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #3b82f6;
                font-weight: bold;
            }
        """)
        
        if self.data_nodes:
            self.table.setColumnCount(len(self.data_nodes) + 2)
            headers = ["#"] + self.data_nodes + ["Actions"]
            self.table.setHorizontalHeaderLabels(headers)
            
            h = self.table.horizontalHeader()
            h.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(0, 54)  # very narrow row number
            
            for i in range(1, len(self.data_nodes) + 1):
                h.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            
            h.setSectionResizeMode(len(self.data_nodes) + 1, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(len(self.data_nodes) + 1, 130)  # compact actions
        
        table_layout.addWidget(self.table)
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #9ca3af; font-size: 13px; padding-top: 12px;")
        table_layout.addWidget(self.stats_label)
        
        layout.addWidget(table_container)

    def _btn_style(self, normal, hover):
        return f"""
            QPushButton {{
                background: {normal};
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
        """

    def refresh_table(self):
        self.table.setRowCount(0)
        if not self.data_nodes:
            return
            
        for row_idx, row_data in enumerate(self.csv_data):
            self.table.insertRow(row_idx)
            
            # Row number
            num_item = QTableWidgetItem(str(row_idx + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            num_item.setFlags(num_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 0, num_item)
            
            # Data
            for col_idx, node in enumerate(self.data_nodes):
                value = row_data.get(node, "")
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx + 1, item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(6, 2, 6, 2)
            actions_layout.setSpacing(8)
            
            edit_btn = QPushButton("edit")
            edit_btn.setFixedSize(54, 30)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-family: "Segoe UI";
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #1d4ed8;
                }
            """)
            edit_btn.setToolTip("Edit this row")
            edit_btn.clicked.connect(lambda _, idx=row_idx: self.edit_row(idx))
            
            delete_btn = QPushButton("delete")
            delete_btn.setFixedSize(54, 30)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #dc2626;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-family: "Segoe UI";
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #b91c1c;
                }
            """)
            delete_btn.setToolTip("Delete this row")
            delete_btn.clicked.connect(lambda _, idx=row_idx: self.delete_row(idx))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row_idx, len(self.data_nodes) + 1, actions_widget)
        
        self.stats_label.setText(
            f"Total rows: {len(self.csv_data)} • "
            f"Columns: {len(self.data_nodes)} • "
            f"Each row = 1 generated PDF"
        )
    
    def add_row(self):
        if not self.data_nodes:
            QMessageBox.warning(self, "No Fields", "Please define data fields first in Design view.")
            return
        dialog = RowDialog(self.data_nodes, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.csv_data.append(dialog.get_data())
            self.save_data()
            self.refresh_table()
    
    def edit_row(self, row_idx):
        if row_idx >= len(self.csv_data):
            return
        dialog = RowDialog(self.data_nodes, self.csv_data[row_idx], parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.csv_data[row_idx] = dialog.get_data()
            self.save_data()
            self.refresh_table()
    
    def delete_row(self, row_idx):
        if row_idx >= len(self.csv_data):
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete row {row_idx + 1}?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.csv_data[row_idx]
            self.save_data()
            self.refresh_table()
    
    def download_schema(self):
        if not self.data_nodes:
            QMessageBox.warning(self, "No Fields", "Define data fields first.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Template CSV", f"{self.project['name']}_template.csv", "CSV (*.csv)"
        )
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.data_nodes)
                    writer.writeheader()
                    writer.writerow({n: f"example_{n}" for n in self.data_nodes})
                QMessageBox.information(self, "Success", f"Template saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def upload_csv(self):
        """Upload CSV file"""
        if not self.data_nodes:
            QMessageBox.warning(
                self,
                "No Data Nodes",
                "Please add data nodes in the design view first!"
            )
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open CSV File",
            "",
            "CSV files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    # Validate headers
                    csv_headers = reader.fieldnames
                    if not csv_headers:
                        raise ValueError("CSV file is empty or has no headers")
                    
                    # Check if all data nodes are in CSV
                    missing = set(self.data_nodes) - set(csv_headers)
                    if missing:
                        raise ValueError(
                            f"CSV is missing these columns: {', '.join(missing)}\n\n"
                            f"Expected columns: {', '.join(self.data_nodes)}"
                        )
                    
                    # Load data
                    new_data = []
                    for row in reader:
                        # Only get the columns we need
                        filtered_row = {node: row.get(node, "") for node in self.data_nodes}
                        new_data.append(filtered_row)
                    
                    if not new_data:
                        raise ValueError("CSV file has no data rows")
                    
                    # Ask to append or replace
                    if self.csv_data:
                        reply = QMessageBox.question(
                            self,
                            "Import Mode",
                            f"Found {len(new_data)} rows in CSV.\n\n"
                            f"Current data: {len(self.csv_data)} rows\n\n"
                            "Do you want to:\n"
                            "• Yes: Replace existing data\n"
                            "• No: Append to existing data",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                        )
                        
                        if reply == QMessageBox.StandardButton.Yes:
                            self.csv_data = new_data
                        elif reply == QMessageBox.StandardButton.No:
                            self.csv_data.extend(new_data)
                        else:
                            return
                    else:
                        self.csv_data = new_data
                    
                    self.save_data()
                    self.refresh_table()
                    
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Loaded {len(new_data)} rows from CSV!\n\nTotal rows: {len(self.csv_data)}"
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Failed to import CSV:\n\n{str(e)}"
                )
    
    def export_csv(self):
        """Export data to CSV"""
        if not self.csv_data:
            QMessageBox.warning(
                self,
                "No Data",
                "No data to export. Please add some rows first!"
            )
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{self.project['name']}_export_{timestamp}.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            default_name,
            "CSV files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.data_nodes)
                    writer.writeheader()
                    writer.writerows(self.csv_data)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Exported {len(self.csv_data)} rows to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export CSV:\n{str(e)}")
    
    def save_data(self):
        self.pdf_data_manager.save_csv_data(self.project["id"], self.csv_data)