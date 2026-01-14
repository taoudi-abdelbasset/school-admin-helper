"""
Base Tool Class - PyQt6 Version
Place in: tools/base_tool_pyqt6.py

Updates:
- Modified header to use separate icon label with font icon
- No description added if empty
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class BaseToolPyQt6(QWidget):
    """
    Base class for all PyQt6 tools
    Inherit from this class when creating new tools
    """
    
    # Tool metadata (override in child classes)
    TOOL_NAME = "Base Tool"
    TOOL_DESCRIPTION = ""
    TOOL_CATEGORY = "Other"
    TOOL_ICON = chr(0xE873)  # Default Material Symbols icon (save_alt)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1a1a1a;")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._create_header()
        self._create_tool_content()
    
    def _create_header(self):
        """Create tool header with title and description"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #242424;
                border-bottom: 1px solid #3a3a3a;
                padding: 20px 30px;
            }
        """)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setSpacing(4)
        
        # Title row with icon
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        icon_label = QLabel(self.TOOL_ICON)
        icon_label.setFont(QFont("Material Symbols Rounded", 28))
        icon_label.setStyleSheet("color: white;")
        title_row.addWidget(icon_label)
        
        title_label = QLabel(self.TOOL_NAME)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        title_row.addWidget(title_label)
        
        title_row.addStretch()
        header_layout.addLayout(title_row)
        
        # Description (if present)
        if self.TOOL_DESCRIPTION:
            desc = QLabel(self.TOOL_DESCRIPTION)
            desc.setStyleSheet("font-size: 14px; color: #b0b0b0; margin-top: 5px;")
            header_layout.addWidget(desc)
        
        self.main_layout.addWidget(header)
    
    def _create_tool_content(self):
        """
        Override this method in child classes to create tool-specific content
        """
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        placeholder = QLabel(
            "Tool content goes here.\nOverride _create_tool_content() method to add your tool's interface."
        )
        placeholder.setStyleSheet("font-size: 14px; color: #b0b0b0;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(placeholder)
        
        self.main_layout.addWidget(content)
    
    def on_open(self):
        """Called when tool is opened"""
        pass
    
    def on_close(self):
        """Called when tool is closed"""
        pass