"""
Main Application - Full PyQt6 Version
Replace main.py with this
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from core.app_pyqt6 import ToolsHelperApp


from config.theme_manager import ThemeManager
from config.language_manager import get_language_manager
from core.data_manager import DataManager

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Tools Helper")
    
    # Load saved settings
    data_manager = DataManager()
    lang_manager = get_language_manager()
    
    # Apply saved language
    saved_lang = data_manager.get_setting("language", "en")
    lang_manager.load_language(saved_lang)
    
    # Apply saved theme
    saved_theme = data_manager.get_setting("theme", "dark")
    ThemeManager.apply_theme(saved_theme)
    
    # Create and show main window
    window = ToolsHelperApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()