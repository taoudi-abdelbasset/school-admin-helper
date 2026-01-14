from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

THEMES = {
    "dark": {
        "window": "#1a1a1a",
        "window_text": "#ffffff",
        "base": "#242424",
        "alternate_base": "#2b2b2b",
        "button": "#2b2b2b",
        "button_text": "#ffffff",
        "highlight": "#1f6aa5",
        "highlighted_text": "#ffffff",
        "sidebar": "#2b2b2b",
        "border": "#3a3a3a"
    },
    "light": {
        "window": "#f5f5f5",
        "window_text": "#000000",
        "base": "#ffffff",
        "alternate_base": "#f0f0f0",
        "button": "#e0e0e0",
        "button_text": "#000000",
        "highlight": "#1f6aa5",
        "highlighted_text": "#ffffff",
        "sidebar": "#e8e8e8",
        "border": "#d0d0d0"
    },
    "vscode": {
        "window": "#1e1e1e",
        "window_text": "#cccccc",
        "base": "#252526",
        "alternate_base": "#2d2d30",
        "button": "#2d2d30",
        "button_text": "#cccccc",
        "highlight": "#0e639c",
        "highlighted_text": "#ffffff",
        "sidebar": "#252526",
        "border": "#3e3e42"
    }
}


class ThemeManager:
    """Manages application themes"""
    
    @staticmethod
    def apply_theme(theme_name="dark"):
        """Apply theme to application"""
        if theme_name not in THEMES:
            theme_name = "dark"
        
        theme = THEMES[theme_name]
        app = QApplication.instance()
        
        if app:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(theme["window"]))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["window_text"]))
            palette.setColor(QPalette.ColorRole.Base, QColor(theme["base"]))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["alternate_base"]))
            palette.setColor(QPalette.ColorRole.Button, QColor(theme["button"]))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["button_text"]))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["highlight"]))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme["highlighted_text"]))
            
            app.setPalette(palette)
            app.setStyle("Fusion")
    
    @staticmethod
    def get_theme_colors(theme_name="dark"):
        """Get theme colors dictionary"""
        return THEMES.get(theme_name, THEMES["dark"])