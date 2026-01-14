"""
Settings Page - Clean separation of themes and languages
Replace ui/settings_page.py
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QFrame, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal

from config.language_manager import get_language_manager
from config.theme_manager import ThemeManager
from config.theme_stylesheet import get_global_stylesheet
from core.data_manager import DataManager


class SettingsPage(QWidget):
    """Settings page with separate theme and language selection"""
    
    settingsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.data_manager = DataManager()
        self.setup_ui()
    
    def setup_ui(self):
        if self.layout():
            QWidget().setLayout(self.layout())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        self.title_label = QLabel(self.lang_manager.get('settings.title', 'Settings'))
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Theme section
        self.theme_label = QLabel(self.lang_manager.get('settings.appearance', 'Theme'))
        self.theme_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.theme_label)
        
        # Theme combo - dynamically loaded from themes.json
        self.theme_combo = QComboBox()
        available_themes = ThemeManager.get_available_themes()
        for theme in available_themes:
            self.theme_combo.addItem(theme["name"], theme["code"])
        
        # Use application stylesheet; avoid inline colors so theme controls appearance
        self.theme_combo.setStyleSheet("")
        
        # Set current theme
        current_theme = self.data_manager.get_setting("theme", "dark")
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        
        layout.addWidget(self.theme_combo)
        
        # Language section
        self.lang_label = QLabel(self.lang_manager.get('settings.language', 'Language'))
        self.lang_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(self.lang_label)
        
        # Language combo - dynamically loaded from languages/
        self.lang_combo = QComboBox()
        languages = self.lang_manager.get_available_languages()
        for lang in languages:
            self.lang_combo.addItem(f"{lang['name']}", lang["code"])
        self.lang_combo.setStyleSheet("")
        
        # Set current language
        current_lang = self.data_manager.get_setting("language", "en")
        lang_index = self.lang_combo.findData(current_lang)
        if lang_index >= 0:
            self.lang_combo.setCurrentIndex(lang_index)
        
        layout.addWidget(self.lang_combo)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.reset_btn = QPushButton(self.lang_manager.get('settings.reset', 'Reset to Defaults'))
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #404040;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #404040;
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
            # Reset to defaults
            self.data_manager.update_setting("language", "en")
            self.data_manager.update_setting("theme", "dark")
            
            # Apply defaults
            self.lang_manager.load_language("en")
            ThemeManager.apply_theme("dark")
            
            # Refresh UI
            self.refresh_labels()
            self.settingsChanged.emit()
            
            QMessageBox.information(
                self,
                self.lang_manager.get('settings.title', 'Settings'),
                self.lang_manager.get('settings.reset_success', 'Settings reset to defaults!')
            )
    
    def save_settings(self):
        # Get selected theme
        theme_code = self.theme_combo.currentData()
        old_theme = self.data_manager.get_setting("theme", "dark")
        
        # Get selected language
        lang_code = self.lang_combo.currentData()
        old_lang = self.data_manager.get_setting("language", "en")
        
        # Save settings
        self.data_manager.update_setting("theme", theme_code)
        self.data_manager.update_setting("language", lang_code)
        
        # Apply theme changes - update both palette and stylesheet
        if theme_code != old_theme:
            ThemeManager.apply_theme(theme_code)
            # Apply the new stylesheet immediately to all widgets
            app = QApplication.instance()
            if app:
                app.setStyleSheet(get_global_stylesheet(theme_code))
                app.processEvents()
            QMessageBox.information(
                self,
                "Theme Changed",
                "Theme changed! All colors updated."
            )
        
        # Apply language changes
        if lang_code != old_lang:
            self.lang_manager.load_language(lang_code)
            self.refresh_labels()
        
        self.settingsChanged.emit()
        
        if theme_code == old_theme and lang_code == old_lang:
            QMessageBox.information(
                self,
                self.lang_manager.get('settings.title', 'Settings'),
                self.lang_manager.get('settings.saved', 'Settings saved successfully!')
            )
    
    def refresh_labels(self):
        """Refresh all labels with new language"""
        self.title_label.setText(self.lang_manager.get('settings.title', 'Settings'))
        self.theme_label.setText(self.lang_manager.get('settings.appearance', 'Theme'))
        self.lang_label.setText(self.lang_manager.get('settings.language', 'Language'))
        
        # Refresh theme combo (names might be translated)
        current_theme_code = self.theme_combo.currentData()
        self.theme_combo.clear()
        available_themes = ThemeManager.get_available_themes()
        for theme in available_themes:
            self.theme_combo.addItem(theme["name"], theme["code"])
        theme_index = self.theme_combo.findData(current_theme_code)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        
        # Refresh language combo
        current_lang_code = self.lang_combo.currentData()
        self.lang_combo.clear()
        languages = self.lang_manager.get_available_languages()
        for lang in languages:
            self.lang_combo.addItem(f"{lang['name']}", lang["code"])
        lang_index = self.lang_combo.findData(current_lang_code)
        if lang_index >= 0:
            self.lang_combo.setCurrentIndex(lang_index)
        
        # Refresh buttons
        self.reset_btn.setText(self.lang_manager.get('settings.reset', 'Reset to Defaults'))
        self.save_btn.setText(self.lang_manager.get('settings.save', 'Save Changes'))