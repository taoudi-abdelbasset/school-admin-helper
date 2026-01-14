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
        
        self._create_tool_content()
    
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