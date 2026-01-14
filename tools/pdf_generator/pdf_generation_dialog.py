"""
PDF Generation Progress Dialog
Place in: tools/pdf_generator/pdf_generation_dialog.py

Shows progress during PDF generation with cancel button
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


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
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # Status message
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #b0b0b0; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #2d2d2d;
                text-align: center;
                color: white;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #2fa572;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Progress text
        self.progress_text = QLabel("0 / 0")
        self.progress_text.setStyleSheet("color: #808080; font-size: 12px;")
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_text)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedWidth(120)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
        """)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.cancel_generation)
        btn_layout.addWidget(self.cancel_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedWidth(120)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1f6aa5;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #144870;
            }
        """)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setVisible(False)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
    
    def update_progress(self, current, total, message):
        """Update progress display"""
        self.progress_bar.setValue(current)
        self.status_label.setText(message)
        self.progress_text.setText(f"{current} / {total}%")
    
    def on_complete(self, output_path):
        """Handle completion"""
        self.is_complete = True
        self.cancel_btn.setVisible(False)
        self.close_btn.setVisible(True)
        
        self.status_label.setText("✅ PDF generation complete!")
        self.status_label.setStyleSheet("color: #2fa572; font-size: 13px; font-weight: bold;")
        
        # Show file location
        file_info = QLabel(f"Saved to:\n{output_path}")
        file_info.setStyleSheet("color: #808080; font-size: 11px;")
        file_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_info.setWordWrap(True)
        self.layout().insertWidget(self.layout().count() - 1, file_info)
    
    def on_error(self, error_message):
        """Handle error"""
        self.is_error = True
        self.cancel_btn.setText("Close")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.reject)
        
        self.status_label.setText(f"❌ {error_message}")
        self.status_label.setStyleSheet("color: #d32f2f; font-size: 12px;")
    
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