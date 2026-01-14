"""
PDF Generation Progress Dialog
Place in: tools/pdf_generator/pdf_generation_dialog.py

Shows progress during PDF generation with cancel button
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from ui.styles import COLORS


class PDFGenerationThread(QThread):
    """Thread for running PDF generation without blocking UI"""
    
    progressUpdated = pyqtSignal(int, int, str)
    generationComplete = pyqtSignal(str)
    generationError = pyqtSignal(str)
    
    def __init__(self, engine, project, pdf_data_manager, output_path):
        super().__init__()
        self.engine = engine
        self.project = project
        self.pdf_data_manager = pdf_data_manager
        self.output_path = output_path
        
        # Connect engine signals
        self.engine.progressUpdated.connect(self.progressUpdated.emit)
        self.engine.generationComplete.connect(self.generationComplete.emit)
        self.engine.generationError.connect(self.generationError.emit)
    
    def run(self):
        """Run generation in thread"""
        self.engine.generate_pdfs(
            self.project,
            self.pdf_data_manager,
            self.output_path
        )


class PDFGenerationDialog(QDialog):
    """Dialog showing PDF generation progress"""
    
    def __init__(self, engine, project, pdf_data_manager, output_path, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.project = project
        self.output_path = output_path
        
        self.setWindowTitle("Generating PDFs...")
        self.setModal(True)
        self.setFixedSize(500, 250)
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint
        )
        
        self.is_complete = False
        self.is_error = False
        
        self.setup_ui()
        
        # Start generation in thread
        self.thread = PDFGenerationThread(
            engine, 
            project, 
            pdf_data_manager, 
            output_path
        )
        self.thread.progressUpdated.connect(self.update_progress)
        self.thread.generationComplete.connect(self.on_complete)
        self.thread.generationError.connect(self.on_error)
        self.thread.start()
    
    def setup_ui(self):
        """Create UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Icon + Title
        header = QFrame()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(10)
        
        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon)
        
        title = QLabel("Generating PDF Pages")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['text_primary']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # Status message
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                background-color: {COLORS['card_bg']};
                text-align: center;
                color: {COLORS['text_primary']};
                height: 30px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['success']};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # Progress text
        self.progress_text = QLabel("0 / 0")
        self.progress_text.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_text)
        
        layout.addStretch()
        
        # Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.cancel_btn.setFixedHeight(36)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: {COLORS['button_text']};
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_secondary']};
            }}
        """)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.cancel_generation)
        self.btn_layout.addWidget(self.cancel_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.close_btn.setFixedHeight(36)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['button_text']};
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setVisible(False)
        self.btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(self.btn_layout)

    def _show_close_fullwidth(self):
        """Replace button area with a single full-width Close button."""
        # Clear existing layout items
        while self.btn_layout.count():
            item = self.btn_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Configure close button to expand
        self.close_btn.setVisible(True)
        self.close_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.close_btn.setFixedHeight(36)
        self.btn_layout.addWidget(self.close_btn)
    
    def update_progress(self, current, total, message):
        """Update progress display"""
        self.progress_bar.setValue(current)
        self.status_label.setText(message)
        self.progress_text.setText(f"{current} / {total}%")
    
    def on_complete(self, output_path):
        """Handle completion"""
        self.is_complete = True
        self.cancel_btn.setVisible(False)
        # Replace button area with single full-width close button
        self._show_close_fullwidth()
        
        self.status_label.setText("✅ PDF generation complete!")
        self.status_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 13px; font-weight: bold;")
        
        # Show file location
        file_info = QLabel(f"Saved to:\n{output_path}")
        file_info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        file_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_info.setWordWrap(True)
        self.layout().insertWidget(self.layout().count() - 1, file_info)
    
    def on_error(self, error_message):
        """Handle error"""
        self.is_error = True
        self.cancel_btn.setText("Close")
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['button_text']};
                border: none;
                padding: 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['card_bg']};
            }}
        """)
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.reject)
        
        self.status_label.setText(f"❌ {error_message}")
        self.status_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 12px;")
    
    def cancel_generation(self):
        """Cancel the generation"""
        self.engine.cancel()
        self.thread.quit()
        self.thread.wait()
        self.reject()
    
    def closeEvent(self, event):
        """Handle close event"""
        if not self.is_complete and not self.is_error:
            event.ignore()
        else:
            event.accept()