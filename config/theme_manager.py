"""
Theme Manager - Reads from themes.json
Place in: config/theme_manager.py
"""
import json
import os
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    """Manages application themes from themes.json"""
    
    _themes = None
    _themes_file = None
    _subscribers = []
    
    @classmethod
    def _load_themes(cls):
        """Load themes from JSON file"""
        if cls._themes is not None:
            return cls._themes
        
        # Find themes.json
        if cls._themes_file is None:
            current_dir = os.path.dirname(__file__)
            cls._themes_file = os.path.join(current_dir, "themes.json")
        
        # Load themes
        try:
            with open(cls._themes_file, 'r', encoding='utf-8') as f:
                cls._themes = json.load(f)
                print(f"✅ Loaded {len(cls._themes)} themes from themes.json")
                return cls._themes
        except FileNotFoundError:
            print(f"⚠️ themes.json not found at {cls._themes_file}")
            print("   Using default dark theme")
            # Fallback to default dark theme
            cls._themes = {
                "dark": {
                    "name": "Dark",
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
                }
            }
            return cls._themes
        except Exception as e:
            print(f"❌ Error loading themes.json: {e}")
            return {}
    
    @classmethod
    def get_available_themes(cls):
        """Get list of available themes"""
        themes = cls._load_themes()
        return [
            {"code": code, "name": data.get("name", code)}
            for code, data in themes.items()
        ]
    
    @classmethod
    def apply_theme(cls, theme_name="dark"):
        """Apply theme to application"""
        themes = cls._load_themes()
        
        if theme_name not in themes:
            print(f"⚠️ Theme '{theme_name}' not found, using 'dark'")
            theme_name = "dark"
        
        theme = themes[theme_name]
        
        print(f"\n🎨 Applying theme: {theme.get('name', theme_name)}")
        
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
            palette.setColor(QPalette.ColorRole.Text, QColor(theme["window_text"]))

            app.setPalette(palette)
            app.setStyle("Fusion")

            # Also apply a theme-aware application stylesheet to cover widgets
            try:
                # import here to avoid circular import at module import time
                from config.theme_stylesheet import get_global_stylesheet
                stylesheet = get_global_stylesheet(theme_name)
                app.setStyleSheet(stylesheet)
            except Exception:
                pass

            # Notify subscribers about theme change
            try:
                for cb in list(cls._subscribers):
                    try:
                        cb(theme_name)
                    except Exception:
                        pass
            except Exception:
                pass

            print(f"✅ Theme '{theme.get('name', theme_name)}' applied\n")
    
    @classmethod
    def get_theme_colors(cls, theme_name="dark"):
        """Get theme colors dictionary"""
        themes = cls._load_themes()
        return themes.get(theme_name, themes.get("dark", {}))

    @classmethod
    def subscribe(cls, callback):
        """Subscribe a callable to theme changes. Callback receives theme_name."""
        if callback not in cls._subscribers:
            cls._subscribers.append(callback)

    @classmethod
    def unsubscribe(cls, callback):
        """Unsubscribe a previously subscribed callback."""
        try:
            cls._subscribers.remove(callback)
        except ValueError:
            pass