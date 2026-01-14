"""
Main Application Window - PyQt6 Version
Place in: core/app_pyqt6.py
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QLabel, QFrame, QPushButton,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from core.tool_manager import get_tool_manager
from core.data_manager import DataManager


class Sidebar(QFrame):
    """Sidebar navigation"""
    
    pageRequested = pyqtSignal(str)  # page_name
    
    def __init__(self, tool_manager, parent=None):
        super().__init__(parent)
        self.tool_manager = tool_manager
        self.data_manager = DataManager()
        self.current_button = None
        
        self.setFixedWidth(250)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-right: 1px solid #3a3a3a;
            }
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border: none;
                background-color: transparent;
                color: #b0b0b0;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1f6aa5;
                color: white;
            }
            QPushButton[selected="true"] {
                background-color: #1f6aa5;
                color: white;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Tools Helper")
        header.setStyleSheet("""
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            color: white;
            background-color: #2b2b2b;
        """)
        layout.addWidget(header)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #3a3a3a;")
        layout.addWidget(sep)
        
        # Main menu
        menu_items = [
            ("🏠 Dashboard", "dashboard"),
            ("⭐ Favorites", "favorites"),
            ("🕐 Recent", "recent"),
        ]
        
        for text, page in menu_items:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, p=page: self.select_page(p))
            btn.setProperty("page_name", page)
            layout.addWidget(btn)
            
            if page == "dashboard":
                self.current_button = btn
                btn.setProperty("selected", True)
                btn.setStyle(btn.style())
        
        # Tools section
        layout.addWidget(self.create_separator())
        
        tools_label = QLabel("🔧 Tools")
        tools_label.setStyleSheet("""
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            color: white;
        """)
        layout.addWidget(tools_label)
        
        # Scrollable tools
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(2)
        
        # Add tools
        all_tools = self.tool_manager.get_all_tools()
        favorites = self.data_manager.get_favorites()
        
        for tool_id, tool_info in all_tools.items():
            btn = self.create_tool_button(tool_id, tool_info, tool_id in favorites)
            scroll_layout.addWidget(btn)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)
        
        # Bottom settings
        layout.addWidget(self.create_separator())
        
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(lambda: self.select_page("settings"))
        settings_btn.setProperty("page_name", "settings")
        layout.addWidget(settings_btn)
    
    def create_tool_button(self, tool_id, tool_info, is_favorite):
        btn = QPushButton(f"{tool_info['icon']} {tool_info['name']}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.select_page(tool_id))
        btn.setProperty("page_name", tool_id)
        return btn
    
    def create_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #3a3a3a; margin: 10px 0;")
        return sep
    
    def select_page(self, page_name):
        # Update buttons
        if self.current_button:
            self.current_button.setProperty("selected", False)
            self.current_button.setStyle(self.current_button.style())
        
        # Find new button
        for btn in self.findChildren(QPushButton):
            if btn.property("page_name") == page_name:
                btn.setProperty("selected", True)
                btn.setStyle(btn.style())
                self.current_button = btn
                break
        
        self.pageRequested.emit(page_name)


class Dashboard(QWidget):
    """Dashboard page"""
    
    def __init__(self, tool_manager, parent=None):
        super().__init__(parent)
        self.tool_manager = tool_manager
        self.data_manager = DataManager()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome
        welcome = QLabel("Welcome to Tools Helper! 👋")
        welcome.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(welcome)
        
        subtitle = QLabel("Your all-in-one toolkit for productivity")
        subtitle.setStyleSheet("font-size: 14px; color: #b0b0b0; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Recent tools
        recent_label = QLabel("Recent Tools")
        recent_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-top: 20px;")
        layout.addWidget(recent_label)
        
        recent_tools = self.data_manager.get_recent_tools()[:3]
        
        if recent_tools:
            for tool_id in recent_tools:
                tool_info = self.tool_manager.get_tool(tool_id)
                if tool_info:
                    card = self.create_tool_card(tool_id, tool_info)
                    layout.addWidget(card)
        else:
            no_tools = QLabel("No recent tools. Browse tools from sidebar!")
            no_tools.setStyleSheet("color: #b0b0b0; padding: 20px;")
            layout.addWidget(no_tools)
        
        layout.addStretch()
    
    def create_tool_card(self, tool_id, tool_info):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #242424;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout(card)
        
        label = QLabel(f"{tool_info['icon']} {tool_info['name']}")
        label.setStyleSheet("font-size: 14px; color: white;")
        layout.addWidget(label, 1)
        
        open_btn = QPushButton("Open")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #1f6aa5;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #144870;
            }
        """)
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(open_btn)
        
        return card


class ToolsHelperApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tools Helper v1.0.0")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 700)
        
        self.tool_manager = get_tool_manager()
        self.data_manager = DataManager()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar(self.tool_manager)
        self.sidebar.pageRequested.connect(self.show_page)
        layout.addWidget(self.sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #1a1a1a;")
        layout.addWidget(self.content_stack, 1)
        
        # Show dashboard
        self.show_page("dashboard")
    
    def show_page(self, page_name):
        # Clear current content
        while self.content_stack.count() > 0:
            widget = self.content_stack.widget(0)
            self.content_stack.removeWidget(widget)
            widget.deleteLater()
        
        # Check if it's a tool
        if page_name in self.tool_manager.tools:
            tool_instance = self.tool_manager.create_tool_instance_pyqt6(page_name)
            if tool_instance:
                self.content_stack.addWidget(tool_instance)
                self.data_manager.add_recent_tool(page_name)
                return
        
        # Built-in pages
        if page_name == "dashboard":
            dashboard = Dashboard(self.tool_manager)
            self.content_stack.addWidget(dashboard)
        else:
            placeholder = self.create_placeholder(page_name)
            self.content_stack.addWidget(placeholder)
    
    def create_placeholder(self, page_name):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel(f"📄 {page_name.title()}")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        msg = QLabel("This page is under construction")
        msg.setStyleSheet("font-size: 16px; color: #b0b0b0; margin-top: 10px;")
        layout.addWidget(msg, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return widget