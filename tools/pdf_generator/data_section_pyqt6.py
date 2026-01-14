"""
Data Section - PyQt6 Version - ALL FIXES
Place in: tools/pdf_generator/data_section_pyqt6.py

FIXES:
✅ CSV import now refreshes table immediately
✅ Download template CSV option added
✅ Excel (.xlsx, .xls) import support
✅ Better font size handling (auto-adjust to fit)
"""
import csv
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDialog, QLineEdit, QFormLayout, QFileDialog, QMessageBox,
    QScrollArea, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

try:
    import qtawesome as qta
except ImportError:
    print("⚠️ qtawesome not installed. Run: pip install qtawesome")
    qta = None

try:
    import openpyxl  # For Excel files
    EXCEL_SUPPORT = True
except ImportError:
    print("⚠️ openpyxl not installed. Excel import disabled. Run: pip install openpyxl")
    EXCEL_SUPPORT = False

from config.language_manager import get_language_manager
from pdf_generator_engine import PDFGeneratorEngine
from pdf_generation_dialog import PDFGenerationDialog
from ui.styles import COLORS

class RowDialog(QDialog):
    """Dialog for adding/editing a data row"""
    
    def __init__(self, data_nodes, row_data=None, parent=None):
        super().__init__(parent)
        
        self.lang_manager = get_language_manager()
        
        self.data_nodes = data_nodes
        self.row_data = row_data or {}
        self.inputs = {}
        
        self.setWindowTitle(
            self.lang_manager.get('pdf_generator.add_row_title', 'Add New Row') 
            if not row_data 
            else self.lang_manager.get('pdf_generator.edit_row_title', 'Edit Row')
        )
        self.setModal(True)
        self.setMinimumWidth(520)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title = QLabel(self.windowTitle())
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['text_primary']};")
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
            label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600; min-width: 140px;")
            
            input_field = QLineEdit()
            input_field.setPlaceholderText(self.lang_manager.get('pdf_generator.enter_value', 'Enter value for') + f" '{node}'")
            input_field.setText(self.row_data.get(node, ""))
            input_field.setStyleSheet(f"""
                QLineEdit {{
                    padding: 8px 12px;
                    background: {COLORS['card_bg']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    color: {COLORS['text_primary']};
                    font-size: 13px;
                }}
                QLineEdit:focus {{
                    border: 1px solid {COLORS['primary']};
                    background: {COLORS['card_bg']};
                }}
            """)
            
            form_layout.addRow(label, input_field)
            self.inputs[node] = input_field
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()
        
        cancel_btn = QPushButton(self.lang_manager.get('common.cancel', 'Cancel'))
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                padding: 8px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton(self.lang_manager.get('common.save', 'Save') if self.row_data else self.lang_manager.get('pdf_generator.add_row', 'Add Row'))
        save_btn.setFixedWidth(100)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['secondary']};
            }}
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
        self.filtered_data = self.csv_data.copy() 
        
        self.lang_manager = get_language_manager()
        
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"background: {COLORS['sidebar_bg']}; border-bottom: 1px solid {COLORS['border']};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 18, 30, 18)
        
        title = QLabel(f"{self.lang_manager.get('pdf_generator.data_table', 'Data Table')} — {self.project['name']}")
        title.setStyleSheet(f"font-size: 19px; font-weight: bold; color: {COLORS['text_primary']};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Back button
        back_btn = QPushButton(f"{self.lang_manager.get('pdf_generator.back_to_design', 'Back to Design')}")
        if qta:
            back_btn.setIcon(qta.icon('fa5s.arrow-left', color='white'))
        back_btn.setFixedHeight(36)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: none;
                padding: 0 16px;
                border-radius: 6px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {COLORS['border']};
            }}
        """)
        back_btn.clicked.connect(lambda: self.backRequested.emit())
        header_layout.addWidget(back_btn)
        
        layout.addWidget(header)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet(f"background: {COLORS['content_bg']}; border-bottom: 1px solid {COLORS['border']};")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(30, 14, 30, 14)
        toolbar_layout.setSpacing(16)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.lang_manager.get('pdf_generator.search', '🔍 Search in table...'))
        self.search_input.setFixedWidth(280)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 12px;
                background: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['primary']};
                background: {COLORS['card_bg']};
            }}
        """)
        self.search_input.textChanged.connect(self.search_table)
        toolbar_layout.addWidget(self.search_input)
        
        # Row count info
        self.row_count_label = QLabel(f"{len(self.csv_data)} {self.lang_manager.get('pdf_generator.rows', 'rows')}")
        self.row_count_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; margin-left: 8px;")
        toolbar_layout.addWidget(self.row_count_label)
        
        toolbar_layout.addStretch()
        
        # Action buttons
        add_btn = self._create_icon_btn(self.lang_manager.get('pdf_generator.add', 'Add'), 'fa5s.plus', "#10b981", "#059669")
        add_btn.clicked.connect(self.add_row)
        toolbar_layout.addWidget(add_btn)
        
        delete_btn = self._create_icon_btn(self.lang_manager.get('pdf_generator.delete', 'Delete'), 'fa5s.trash', "#dc2626", "#b91c1c")
        delete_btn.clicked.connect(self.delete_selected_rows)
        toolbar_layout.addWidget(delete_btn)
        
        toolbar_layout.addWidget(self._create_v_separator())
        
        # 🆕 Download Template button
        download_template_btn = self._create_icon_btn(
            self.lang_manager.get('pdf_generator.download_template', 'Template'), 
            'fa5s.download', 
            "#f59e0b", 
            "#d97706"
        )
        download_template_btn.clicked.connect(self.download_schema)
        toolbar_layout.addWidget(download_template_btn)
        
        # Import button with Excel support
        import_text = self.lang_manager.get('pdf_generator.import_csv', 'Import CSV/Excel' if EXCEL_SUPPORT else 'Import CSV')
        import_btn = self._create_icon_btn(import_text, 'fa5s.file-import', "#3b82f6", "#2563eb")
        import_btn.clicked.connect(self.upload_csv)
        toolbar_layout.addWidget(import_btn)
        
        export_btn = self._create_icon_btn(self.lang_manager.get('pdf_generator.export', 'Export'), 'fa5s.file-export', "#8b5cf6", "#7c3aed")
        export_btn.clicked.connect(self.export_csv)
        toolbar_layout.addWidget(export_btn)
        
        toolbar_layout.addWidget(self._create_v_separator())
        
        # Generate PDF
        pdf_btn = self._create_icon_btn(self.lang_manager.get('pdf_generator.generate_pdfs', 'Generate PDFs'), 'fa5s.file-pdf', "#ef4444", "#dc2626")
        pdf_btn.clicked.connect(self.generate_pdf)
        toolbar_layout.addWidget(pdf_btn)
        
        layout.addWidget(toolbar)
        
        # Table area
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(30, 20, 30, 20)
        
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {COLORS['content_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text_primary']};
                gridline-color: {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background: {COLORS['primary']};
            }}
            QHeaderView::section {{
                background: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {COLORS['primary']};
                font-weight: bold;
            }}
        """)
        
        if self.data_nodes:
            self.table.setColumnCount(len(self.data_nodes) + 2)
            headers = ["#"] + self.data_nodes + [self.lang_manager.get('common.actions', 'Actions')]
            self.table.setHorizontalHeaderLabels(headers)
            
            h = self.table.horizontalHeader()
            h.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(0, 50)
            
            for i in range(1, len(self.data_nodes) + 1):
                h.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            
            h.setSectionResizeMode(len(self.data_nodes) + 1, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(len(self.data_nodes) + 1, 150)
        
        table_layout.addWidget(self.table)
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; padding-top: 12px;")
        table_layout.addWidget(self.stats_label)
        
        layout.addWidget(table_container)

    def search_table(self):
        """Filter table based on search query"""
        search_text = self.search_input.text().strip().lower()
        
        if not search_text:
            self.filtered_data = self.csv_data.copy()
        else:
            self.filtered_data = []
            for row_data in self.csv_data:
                row_values = " ".join(str(v).lower() for v in row_data.values())
                if search_text in row_values:
                    self.filtered_data.append(row_data)
        
        self.row_count_label.setText(
            f"{len(self.filtered_data)}/{len(self.csv_data)} rows"
        )
        
        self.refresh_table()
        
    def _create_icon_btn(self, text, icon_name, normal, hover):
        btn = QPushButton(f" {text}")
        if qta:
            btn.setIcon(qta.icon(icon_name, color='white'))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {normal};
                color: {COLORS['text_primary']};
                border: none;
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
    
    def _create_v_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"background: {COLORS['border']}; margin: 0 8px;")
        sep.setFixedWidth(1)
        return sep

    def refresh_table(self):
        self.table.setRowCount(0)
        if not self.data_nodes:
            return
        
        display_data = self.filtered_data if hasattr(self, 'filtered_data') else self.csv_data
        
        for display_idx, row_data in enumerate(display_data):
            original_idx = self.csv_data.index(row_data)
            
            self.table.insertRow(display_idx)
            self.table.setRowHeight(display_idx, 50)
            
            # Row number
            num_item = QTableWidgetItem(str(original_idx + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            num_item.setFlags(num_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(display_idx, 0, num_item)
            
            # Data
            for col_idx, node in enumerate(self.data_nodes):
                value = row_data.get(node, "")
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(display_idx, col_idx + 1, item)
            
            # Actions
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background: transparent;")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(6, 4, 6, 4)
            actions_layout.setSpacing(6)
            
            edit_btn = QPushButton()
            if qta:
                edit_btn.setIcon(qta.icon('fa5s.edit', color='white'))
            else:
                edit_btn.setText("Edit")
            edit_btn.setFixedSize(32, 28)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['primary']};
                    color: {COLORS['text_primary']};
                    border: none;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background: {COLORS['secondary']};
                }}
            """)
            edit_btn.setToolTip("Edit this row")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda _, idx=original_idx: self.edit_row(idx))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton()
            if qta:
                delete_btn.setIcon(qta.icon('fa5s.trash', color='white'))
            else:
                delete_btn.setText("Del")
            delete_btn.setFixedSize(32, 28)
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['danger']};
                    color: {COLORS['text_primary']};
                    border: none;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background: #b91c1c;
                }}
            """)
            delete_btn.setToolTip("Delete this row")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(lambda _, idx=original_idx: self.delete_row(idx))
            actions_layout.addWidget(delete_btn)
            
            actions_layout.addStretch()
            
            self.table.setCellWidget(display_idx, len(self.data_nodes) + 1, actions_widget)
        
        # Update stats
        if hasattr(self, 'filtered_data') and len(self.filtered_data) != len(self.csv_data):
            self.stats_label.setText(
                f"Showing {len(self.filtered_data)} of {len(self.csv_data)} rows • "
                f"Columns: {len(self.data_nodes)}"
            )
        else:
            self.stats_label.setText(
                f"Total rows: {len(self.csv_data)} • "
                f"Columns: {len(self.data_nodes)} • "
                f"Each row = 1 generated PDF"
            )
            
    def add_row(self):
        if not self.data_nodes:
            QMessageBox.warning(self, self.lang_manager.get('pdf_generator.no_data_nodes', 'No Data Nodes'), 
                                self.lang_manager.get('pdf_generator.add_data_nodes_msg', 'Please add data nodes in the design view first!'))
            return
        dialog = RowDialog(self.data_nodes, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.csv_data.append(dialog.get_data())
            self.save_data()
            self.search_input.clear()
            self.filtered_data = self.csv_data.copy()
            self.refresh_table()
    
    def edit_row(self, row_idx):
        if row_idx >= len(self.csv_data):
            return
        dialog = RowDialog(self.data_nodes, self.csv_data[row_idx], parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.csv_data[row_idx] = dialog.get_data()
            self.save_data()
            self.search_table()
    
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
            self.filtered_data = self.csv_data.copy()
            self.save_data()
            self.search_table()
    
    def delete_selected_rows(self):
        """Delete all selected rows"""
        selected_display_rows = []
        for index in self.table.selectionModel().selectedRows():
            selected_display_rows.append(index.row())
        
        if not selected_display_rows:
            QMessageBox.warning(self, self.lang_manager.get('common.error', 'Error'), 
                                self.lang_manager.get('pdf_generator.no_selection', 'Please select rows to delete.\n\nTip: Click on rows to select them (Ctrl+Click for multiple).'))
            return
        
        display_data = self.filtered_data if hasattr(self, 'filtered_data') else self.csv_data
        
        rows_to_delete = []
        for display_idx in selected_display_rows:
            if display_idx < len(display_data):
                row_data = display_data[display_idx]
                rows_to_delete.append(row_data)
        
        if not rows_to_delete:
            return
        
        row_count = len(rows_to_delete)
        reply = QMessageBox.question(
            self, self.lang_manager.get('pdf_generator.confirm_delete', 'Confirm Delete'),
            self.lang_manager.get('pdf_generator.delete_rows_message', f"Are you sure you want to delete {row_count} selected row{'s' if row_count > 1 else ''}?\n\nThis cannot be undone."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for row_data in rows_to_delete:
                if row_data in self.csv_data:
                    self.csv_data.remove(row_data)
            
            self.filtered_data = self.csv_data.copy()
            self.save_data()
            self.search_table()
            
            QMessageBox.information(
                self, self.lang_manager.get('pdf_generator.success', 'Success'), 
                self.lang_manager.get('pdf_generator.rows_deleted', f"Deleted {row_count} row{'s' if row_count > 1 else ''} successfully!")
            )
    
    def download_schema(self):
        """🆕 Download template CSV with headers"""
        if not self.data_nodes:
            QMessageBox.warning(
                self, 
                "No Data Nodes", 
                "Please add data nodes in the design view first!\n\nData nodes define the columns for your CSV template."
            )
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{self.project['name']}_template_{timestamp}.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Template CSV", 
            default_name, 
            "CSV files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.data_nodes)
                    writer.writeheader()
                    # Add one example row
                    example_row = {node: f"example_{node}" for node in self.data_nodes}
                    writer.writerow(example_row)
                
                QMessageBox.information(
                    self, 
                    "Template Downloaded", 
                    f"Template CSV saved with headers:\n\n{', '.join(self.data_nodes)}\n\nFile: {file_path}\n\n"
                    "Fill in your data and import it back!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create template:\n{str(e)}")
    
    def upload_csv(self):
        """🆕 Import CSV or Excel files"""
        if not self.data_nodes:
            QMessageBox.warning(
                self, 
                "No Data Nodes", 
                "Please add data nodes in the design view first!"
            )
            return
        
        # File filter based on Excel support
        if EXCEL_SUPPORT:
            file_filter = "Data files (*.csv *.xlsx *.xls);;CSV files (*.csv);;Excel files (*.xlsx *.xls)"
        else:
            file_filter = "CSV files (*.csv)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Import Data File", 
            "", 
            file_filter
        )
        
        if not file_path:
            return
        
        try:
            # Determine file type
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                new_data = self._import_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                if not EXCEL_SUPPORT:
                    raise ValueError("Excel support not available. Please install openpyxl: pip install openpyxl")
                new_data = self._import_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            if not new_data:
                raise ValueError("No data rows found in file")
            
            # Ask user what to do with existing data
            if self.csv_data:
                reply = QMessageBox.question(
                    self, 
                    "Import Mode",
                    f"Found {len(new_data)} rows in file.\n\n"
                    f"Current data: {len(self.csv_data)} rows\n\n"
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
            
            # 🔧 FIX: Refresh immediately after import
            self.filtered_data = self.csv_data.copy()
            self.save_data()
            
            # Clear search and refresh table
            self.search_input.clear()
            self.refresh_table()
            
            # Update row count label
            self.row_count_label.setText(f"{len(self.csv_data)} rows")
            
            QMessageBox.information(
                self, 
                "Import Successful",
                f"Imported {len(new_data)} rows from {os.path.basename(file_path)}!\n\n"
                f"Total rows now: {len(self.csv_data)}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Import Error", 
                f"Failed to import file:\n\n{str(e)}"
            )
    
    def _import_csv(self, file_path):
        """Import data from CSV file"""
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_headers = reader.fieldnames
            
            if not csv_headers:
                raise ValueError("CSV file is empty or has no headers")
            
            # Check for missing columns
            missing = set(self.data_nodes) - set(csv_headers)
            if missing:
                raise ValueError(
                    f"CSV is missing these columns:\n{', '.join(missing)}\n\n"
                    f"Expected columns:\n{', '.join(self.data_nodes)}"
                )
            
            # Filter to only include expected columns
            new_data = []
            for row in reader:
                filtered_row = {node: row.get(node, "") for node in self.data_nodes}
                new_data.append(filtered_row)
            
            return new_data
    
    def _import_excel(self, file_path):
        """🆕 Import data from Excel file"""
        workbook = openpyxl.load_workbook(file_path, read_only=True)
        sheet = workbook.active
        
        # Get headers from first row
        headers = []
        for cell in sheet[1]:
            headers.append(str(cell.value).strip() if cell.value else "")
        
        if not headers or not any(headers):
            raise ValueError("Excel file has no headers in first row")
        
        # Check for missing columns
        missing = set(self.data_nodes) - set(headers)
        if missing:
            raise ValueError(
                f"Excel is missing these columns:\n{', '.join(missing)}\n\n"
                f"Expected columns:\n{', '.join(self.data_nodes)}"
            )
        
        # Map header names to column indices
        header_map = {header: idx for idx, header in enumerate(headers)}
        
        # Read data rows (skip header row)
        new_data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            filtered_row = {}
            for node in self.data_nodes:
                col_idx = header_map.get(node, -1)
                if col_idx >= 0 and col_idx < len(row):
                    value = row[col_idx]
                    # Convert None to empty string
                    filtered_row[node] = str(value).strip() if value is not None else ""
                else:
                    filtered_row[node] = ""
            
            # Skip completely empty rows
            if any(filtered_row.values()):
                new_data.append(filtered_row)
        
        workbook.close()
        return new_data
    
    def export_csv(self):
        """Export data to CSV"""
        if not self.csv_data:
            QMessageBox.warning(
                self, 
                self.lang_manager.get('common.error', 'Error'), 
                self.lang_manager.get('pdf_generator.no_data_export', 'No data to export. Please add some rows first!')
            )
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{self.project['name']}_export_{timestamp}.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            self.lang_manager.get('pdf_generator.export', 'Export'), 
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
                    self.lang_manager.get('pdf_generator.success', 'Success'), 
                    f"{self.lang_manager.get('pdf_generator.export_success', 'Exported')} {len(self.csv_data)} {self.lang_manager.get('pdf_generator.rows', 'rows')} to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    self.lang_manager.get('common.error', 'Error'), 
                    f"{self.lang_manager.get('pdf_generator.export_failed', 'Failed to export CSV')}:\n{str(e)}"
                )
    
    def save_data(self):
        """Save data to file"""
        self.pdf_data_manager.save_csv_data(self.project["id"], self.csv_data)

    def generate_pdf(self):
        """Generate PDF from current data"""
        if not self.csv_data:
            QMessageBox.warning(
                self, 
                self.lang_manager.get('common.error', 'Error'),
                self.lang_manager.get('pdf_generator.no_data_generate', 'No data to generate PDFs from.\n\nPlease add some data rows first!')
            )
            return
        
        # Get output file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{self.project['name']}_output_{timestamp}.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.lang_manager.get('pdf_generator.save_generated_pdf', 'Save Generated PDF'),
            default_name,
            "PDF files (*.pdf)"
        )
        
        if not file_path:
            return
        
        # Create engine and show progress dialog
        engine = PDFGeneratorEngine()
        
        dialog = PDFGenerationDialog(
            engine,
            self.project,
            self.pdf_data_manager,
            file_path,
            parent=self
        )
        
        result = dialog.exec()
        
        if dialog.is_complete:
            reply = QMessageBox.information(
                self,
                self.lang_manager.get('pdf_generator.success', 'Success'),
                self.lang_manager.get(
                    'pdf_generator.pdf_generated',
                    f'Successfully generated {len(self.csv_data)} PDF pages!\n\nSaved to:\n{file_path}\n\nWould you like to open the file?'
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Open file with default PDF viewer
                try:
                    import subprocess
                    import platform
                    
                    if platform.system() == 'Windows':
                        os.startfile(file_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', file_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', file_path])
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        self.lang_manager.get('common.error', 'Error'),
                        f"{self.lang_manager.get('pdf_generator.open_failed', 'Could not open PDF')}:\n{str(e)}"
                    )