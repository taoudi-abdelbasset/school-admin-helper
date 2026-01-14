"""
Main Application - Full PyQt6 Version
Replace main.py with this
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from core.app_pyqt6 import ToolsHelperApp


def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Tools Helper")
    
    # Set dark theme
    app.setStyle("Fusion")
    from PyQt6.QtGui import QPalette, QColor
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(26, 26, 26))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(36, 36, 36))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(31, 106, 165))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(31, 106, 165))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)
    
    # Create and show main window
    window = ToolsHelperApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()