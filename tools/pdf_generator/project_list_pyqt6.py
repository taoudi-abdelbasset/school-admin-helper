"""
Project List Section - With Translation Support
Replace tools/pdf_generator/project_list_pyqt6.py with this
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QTextEdit,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from datetime import datetime
import os
import base64

from config.language_manager import get_language_manager
from ui.styles import COLORS


class ProjectModal(QDialog):
    """Compact modal dialog for creating/editing projects"""
    
    def __init__(self, mode="create", project_data=None, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.project_data = project_data or {}
        self.pdf_file_path = None
        self.pdf_file_data = None
        self.lang_manager = get_language_manager()
        
        title_key = 'pdf_generator.create_project' if mode == "create" else 'pdf_generator.edit_project'
        self.setWindowTitle(self.lang_manager.get(title_key, "Create New Project" if mode == "create" else "Edit Project"))
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.setup_ui()
        
        if mode == "edit" and project_data:
            self.populate_fields()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Title
        icon = "📄" if self.mode == "create" else "✏️"
        title = QLabel(f"{icon} {self.windowTitle()}")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Project Name
        name_label = QLabel(f"{self.lang_manager.get('pdf_generator.project_name', 'Project Name')} *")
        name_label.setStyleSheet(f"font-weight: bold; color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(name_label)
        
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText("e.g., Student ID Cards")
        self.name_entry.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 12px;
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.name_entry)
        
        # Description
        desc_label = QLabel(self.lang_manager.get('pdf_generator.description', 'Description'))
        desc_label.setStyleSheet(f"font-weight: bold; color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(desc_label)
        
        self.desc_textbox = QTextEdit()
        self.desc_textbox.setPlaceholderText("Optional description...")
        self.desc_textbox.setMaximumHeight(70)
        self.desc_textbox.setStyleSheet(f"""
            QTextEdit {{
                padding: 8px 12px;
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                color: {COLORS['text_primary']};
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.desc_textbox)
        
        # PDF File
        pdf_label = QLabel(f"{self.lang_manager.get('pdf_generator.pdf_template', 'PDF Template')} *")
        pdf_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 12px;")
        layout.addWidget(pdf_label)
        
        pdf_frame = QFrame()
        pdf_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        pdf_layout = QHBoxLayout(pdf_frame)
        pdf_layout.setContentsMargins(8, 4, 8, 4)
        
        self.pdf_filename_label = QLabel(self.lang_manager.get('pdf_generator.no_file', 'No file selected'))
        self.pdf_filename_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        pdf_layout.addWidget(self.pdf_filename_label, 1)
        
        select_pdf_btn = QPushButton(self.lang_manager.get('pdf_generator.browse', 'Browse...'))
        select_pdf_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['border']};
                color: {COLORS['text_primary']};
                border: none;
                padding: 6px 16px;
                border-radius: 3px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['card_bg']};
            }}
        """)
        select_pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        select_pdf_btn.clicked.connect(self.select_pdf_file)
        pdf_layout.addWidget(select_pdf_btn)
        
        layout.addWidget(pdf_frame)
        
        layout.addStretch()
        
        # Buttons
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton(self.lang_manager.get('pdf_generator.cancel', 'Cancel'))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b0b0b0;
                border: 1px solid #404040;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
                color: white;
            }
        """)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_text = self.lang_manager.get('pdf_generator.create' if self.mode == "create" else 'pdf_generator.save', 
                                          "Create" if self.mode == "create" else "Save")
        save_btn = QPushButton(save_text)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1f6aa5;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #144870;
            }
        """)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_project)
        btn_layout.addWidget(save_btn)
        
        layout.addWidget(btn_frame)
    
    def populate_fields(self):
        """Populate fields for editing"""
        self.name_entry.setText(self.project_data.get("name", ""))
        desc = self.project_data.get("description", "")
        if desc:
            self.desc_textbox.setPlainText(desc)
        
        pdf_name = self.project_data.get("pdf_file_name")
        if pdf_name:
            self.pdf_filename_label.setText(f"📎 {pdf_name}")
            self.pdf_filename_label.setStyleSheet("color: #2fa572; font-size: 12px;")
    
    def select_pdf_file(self):
        """Open file dialog to select PDF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF Template File",
            "",
            "PDF files (*.pdf);;All files (*.*)"
        )
        
        if file_path:
            self.pdf_file_path = file_path
            filename = os.path.basename(file_path)
            
            try:
                with open(file_path, 'rb') as f:
                    self.pdf_file_data = base64.b64encode(f.read()).decode()
                
                self.pdf_filename_label.setText(f"📎 {filename}")
                self.pdf_filename_label.setStyleSheet("color: #2fa572; font-size: 12px;")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read PDF: {str(e)}")
    
    def save_project(self):
        """Validate and save"""
        name = self.name_entry.text().strip()
        description = self.desc_textbox.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Required Field", "Please enter a project name")
            self.name_entry.setFocus()
            return
        
        if self.mode == "create" and not self.pdf_file_data:
            QMessageBox.warning(self, "Required Field", "Please select a PDF template file")
            return
        
        self.result_data = {
            "name": name,
            "description": description
        }
        
        if self.pdf_file_data:
            self.result_data["pdf_file_name"] = os.path.basename(self.pdf_file_path)
            self.result_data["pdf_file_data"] = self.pdf_file_data
        
        self.accept()


class ProjectListSectionPyQt6(QWidget):
    """Project list section with translation support"""
    
    def __init__(self, data_manager, pdf_data_manager, on_open_project, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.pdf_data_manager = pdf_data_manager
        self.on_open_project = on_open_project
        self.lang_manager = get_language_manager()
        
        self.projects = []
        self.load_projects()
        self.setup_ui()
    
    def load_projects(self):
        """Load projects"""
        self.projects = self.pdf_data_manager.load_projects_list()
    
    def setup_ui(self):
        """Create UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header Bar
        header_bar = QFrame()
        header_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['sidebar_bg']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        title = QLabel(f"📂 {self.lang_manager.get('pdf_generator.projects', 'Projects')}")
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COLORS['text_primary']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        create_btn = QPushButton(f"➕ {self.lang_manager.get('pdf_generator.new_project', 'New Project')}")
        create_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self.open_create_modal)
        header_layout.addWidget(create_btn)
        
        layout.addWidget(header_bar)
        
        # Projects area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background-color: {COLORS['content_bg']};")
        
        self.projects_container = QWidget()
        self.projects_layout = QVBoxLayout(self.projects_container)
        self.projects_layout.setContentsMargins(30, 20, 30, 20)
        self.projects_layout.setSpacing(10)
        self.projects_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.projects_container)
        layout.addWidget(scroll)
        
        self.refresh_projects_display()
    
    def refresh_projects_display(self):
        """Refresh display"""
        # Clear
        while self.projects_layout.count():
            item = self.projects_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.projects:
            self.show_empty_state()
        else:
            self.show_projects_list()
    
    def show_empty_state(self):
        """Show empty state"""
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("📁")
        icon.setStyleSheet("font-size: 72px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(icon)
        
        empty_layout.addSpacing(20)
        
        title = QLabel(self.lang_manager.get('pdf_generator.no_projects', 'No Projects Yet'))
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['text_primary']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(title)
        
        subtitle = QLabel(self.lang_manager.get('pdf_generator.no_projects_desc', 'Create your first PDF template project to get started'))
        subtitle.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']}; margin-top: 8px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(subtitle)
        
        self.projects_layout.addWidget(empty_widget)
    
    def show_projects_list(self):
        """Show projects as clean rows"""
        for project in self.projects:
            row = self.create_project_row(project)
            self.projects_layout.addWidget(row)
    
    def create_project_row(self, project):
        """Create a single project row"""
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
            QFrame:hover {{
                background-color: {COLORS['content_bg']};
                border: 1px solid {COLORS['border']};
            }}
        """)
        row.setMinimumHeight(80)
        row.setMaximumHeight(80)
        
        layout = QHBoxLayout(row)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel("📄")
        icon_label.setStyleSheet(f"font-size: 32px; color: {COLORS['text_primary']};")
        icon_label.setFixedSize(40, 40)
        layout.addWidget(icon_label)
        
        # Info section
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        # Name
        name_label = QLabel(project["name"])
        name_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLORS['text_primary']};")
        info_layout.addWidget(name_label)
        
        # Description + Date
        desc_text = project.get("description", "No description")
        if len(desc_text) > 80:
            desc_text = desc_text[:77] + "..."
        
        meta_text = f"{desc_text} • Created {project['created_at']}"
        meta_label = QLabel(meta_text)
        meta_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        info_layout.addWidget(meta_label)
        
        layout.addWidget(info_widget, 1)
        
        # PDF indicator
        has_pdf = project.get("pdf_file_name") is not None
        pdf_indicator = QLabel("✓ PDF" if has_pdf else "⚠ No PDF")
        pdf_indicator.setStyleSheet(
            f"font-size: 11px; color: {COLORS['success'] if has_pdf else COLORS['warning']}; font-weight: bold;"
        )
        layout.addWidget(pdf_indicator)
        
        # Action buttons
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)
        
        # Design button
        design_btn = QPushButton(f"🎨 {self.lang_manager.get('pdf_generator.design', 'Design')}")
        design_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        design_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        design_btn.clicked.connect(lambda: self.on_open_project(project["id"]))
        btn_layout.addWidget(design_btn)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(36, 36)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['border']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['card_bg']};
            }}
        """)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self.open_edit_modal(project))
        btn_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(36, 36)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['danger']};
                border: 1px solid {COLORS['danger']};
                border-radius: 4px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
                color: {COLORS['text_primary']};
            }}
        """)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.confirm_delete(project))
        btn_layout.addWidget(delete_btn)
        
        layout.addWidget(btn_container)
        
        return row
    
    def open_create_modal(self):
        """Open create modal"""
        modal = ProjectModal(mode="create", parent=self)
        if modal.exec() == QDialog.DialogCode.Accepted:
            self.handle_create_project(modal.result_data)
    
    def open_edit_modal(self, project):
        """Open edit modal"""
        modal = ProjectModal(mode="edit", project_data=project, parent=self)
        if modal.exec() == QDialog.DialogCode.Accepted:
            self.handle_edit_project(project["id"], modal.result_data)
    
    def handle_create_project(self, data):
        """Handle project creation"""
        project_id = f"proj_{int(datetime.now().timestamp())}"
        
        project_meta = {
            "id": project_id,
            "name": data["name"],
            "description": data["description"],
            "pdf_file_name": data.get("pdf_file_name"),
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.pdf_data_manager.add_project_to_list(project_meta)
        self.pdf_data_manager.create_project_folder(project_id)
        
        if data.get("pdf_file_data"):
            self.pdf_data_manager.save_pdf_file(
                project_id,
                data["pdf_file_data"],
                data["pdf_file_name"]
            )
        
        config = {"fields": []}
        self.pdf_data_manager.save_project_config(project_id, config)
        
        self.load_projects()
        self.refresh_projects_display()
        
        QMessageBox.information(
            self, 
            self.lang_manager.get('pdf_generator.success', 'Success'),
            f"{self.lang_manager.get('pdf_generator.project_created', 'Project created!')}"
        )
    
    def handle_edit_project(self, project_id, data):
        """Handle project edit"""
        updates = {
            "name": data["name"],
            "description": data["description"]
        }
        
        if data.get("pdf_file_name"):
            updates["pdf_file_name"] = data["pdf_file_name"]
            self.pdf_data_manager.save_pdf_file(
                project_id,
                data["pdf_file_data"],
                data["pdf_file_name"]
            )
        
        self.pdf_data_manager.update_project_in_list(project_id, updates)
        
        self.load_projects()
        self.refresh_projects_display()
        
        QMessageBox.information(
            self,
            self.lang_manager.get('pdf_generator.success', 'Success'),
            f"{self.lang_manager.get('pdf_generator.project_updated', 'Project updated!')}"
        )
    
    def confirm_delete(self, project):
        """Confirm and delete"""
        reply = QMessageBox.question(
            self,
            self.lang_manager.get('pdf_generator.confirm_delete', 'Confirm Delete'),
            f"{self.lang_manager.get('pdf_generator.delete_message', 'Are you sure you want to delete this project? This action cannot be undone.')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.pdf_data_manager.delete_project(project["id"])
            self.load_projects()
            self.refresh_projects_display()
            QMessageBox.information(
                self,
                self.lang_manager.get('pdf_generator.success', 'Success'),
                f"{self.lang_manager.get('pdf_generator.project_deleted', 'Project deleted.')}"
            )