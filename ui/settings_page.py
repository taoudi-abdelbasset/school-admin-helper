"""
Settings Page - FIXED refresh_labels bug
Replace ui/settings_page.py with this
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from config.language_manager import get_language_manager
from config.theme_manager import ThemeManager
from core.data_manager import DataManager


class SettingsPage(QWidget):
    """Simplified settings page with dropdowns"""
    
    settingsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.data_manager = DataManager()
        self.setup_ui()
    
    def setup_ui(self):
        # Clear existing layout if any
        if self.layout():
            QWidget().setLayout(self.layout())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        self.title_label = QLabel(self.lang_manager.get('settings.title', 'Settings'))
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(self.title_label)
        
        # Theme section
        self.theme_label = QLabel(self.lang_manager.get('settings.appearance', 'Theme'))
        self.theme_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        layout.addWidget(self.theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            self.lang_manager.get('settings.dark', 'Dark'),
            self.lang_manager.get('settings.light', 'Light'),
            self.lang_manager.get('settings.vscode', 'VS Code')
        ])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                background: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                color: white;
            }
            QComboBox:hover {
                border: 1px solid #505050;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #2d2d2d;
                border: 1px solid #404040;
                color: white;
            }
        """)
        # Set current theme
        current_theme = self.data_manager.get_setting("theme", "dark")
        theme_index = {"dark": 0, "light": 1, "vscode": 2}.get(current_theme, 0)
        self.theme_combo.setCurrentIndex(theme_index)
        layout.addWidget(self.theme_combo)
        
        # Language section
        self.lang_label = QLabel(self.lang_manager.get('settings.language', 'Language'))
        self.lang_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0; margin-top: 20px;")
        layout.addWidget(self.lang_label)
        
        self.lang_combo = QComboBox()
        languages = self.lang_manager.get_available_languages()
        for lang in languages:
            self.lang_combo.addItem(f"{lang['name']}", lang["code"])
        self.lang_combo.setStyleSheet(self.theme_combo.styleSheet())
        
        # Set current language
        current_lang = self.data_manager.get_setting("language", "en")
        index = self.lang_combo.findData(current_lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        layout.addWidget(self.lang_combo)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.reset_btn = QPushButton(self.lang_manager.get('settings.reset', 'Reset to Defaults'))
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #b0b0b0;
                border: 1px solid #404040;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #404040;
                color: white;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_settings)
        btn_layout.addWidget(self.reset_btn)
        
        btn_layout.addStretch()
        
        self.save_btn = QPushButton(self.lang_manager.get('settings.save', 'Save Changes'))
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #1f6aa5;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #144870;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
    
    def reset_settings(self):
        reply = QMessageBox.question(
            self,
            self.lang_manager.get('settings.reset_confirm', 'Reset Settings'),
            self.lang_manager.get('settings.reset_message', 'Are you sure you want to reset all settings to defaults?'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.update_setting("language", "en")
            self.data_manager.update_setting("theme", "dark")
            
            self.lang_manager.load_language("en")
            ThemeManager.apply_theme("dark")
            
            self.refresh_labels()
            self.settingsChanged.emit()
            
            QMessageBox.information(
                self,
                self.lang_manager.get('settings.title', 'Settings'),
                self.lang_manager.get('settings.reset_success', 'Settings reset to defaults!')
            )
    
    def save_settings(self):
        theme_map = {0: "dark", 1: "light", 2: "vscode"}
        theme_name = theme_map.get(self.theme_combo.currentIndex(), "dark")
        self.data_manager.update_setting("theme", theme_name)
        ThemeManager.apply_theme(theme_name)
        
        lang_code = self.lang_combo.currentData()
        old_lang = self.data_manager.get_setting("language", "en")
        
        self.data_manager.update_setting("language", lang_code)
        self.lang_manager.load_language(lang_code)
        
        if lang_code != old_lang:
            self.refresh_labels()
        
        self.settingsChanged.emit()
        
        QMessageBox.information(
            self,
            self.lang_manager.get('settings.title', 'Settings'),
            self.lang_manager.get('settings.saved', 'Settings saved successfully!')
        )
    
    def refresh_labels(self):
        """Refresh all labels with new language - FIXED VERSION"""
        # Update title
        self.title_label.setText(self.lang_manager.get('settings.title', 'Settings'))
        
        # Update section labels
        self.theme_label.setText(self.lang_manager.get('settings.appearance', 'Theme'))
        self.lang_label.setText(self.lang_manager.get('settings.language', 'Language'))
        
        # Update combo boxes
        current_theme_idx = self.theme_combo.currentIndex()
        self.theme_combo.clear()
        self.theme_combo.addItems([
            self.lang_manager.get('settings.dark', 'Dark'),
            self.lang_manager.get('settings.light', 'Light'),
            self.lang_manager.get('settings.vscode', 'VS Code')
        ])
        self.theme_combo.setCurrentIndex(current_theme_idx)
        
        # Update language combo
        current_lang_code = self.lang_combo.currentData()
        self.lang_combo.clear()
        languages = self.lang_manager.get_available_languages()
        for lang in languages:
            self.lang_combo.addItem(f"{lang['name']}", lang["code"])
        index = self.lang_combo.findData(current_lang_code)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        
        # Update buttons
        self.reset_btn.setText(self.lang_manager.get('settings.reset', 'Reset to Defaults'))
        self.save_btn.setText(self.lang_manager.get('settings.save', 'Save Changes'))