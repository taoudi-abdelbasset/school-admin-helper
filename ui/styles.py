"""
UI Styles and Constants
"""
from config.theme_manager import ThemeManager
from core.data_manager import DataManager

# Get current theme
data_manager = DataManager()
current_theme = data_manager.get_setting("theme", "dark")

# Colors - dynamically loaded from theme (populated by reload_theme)
COLORS = {}


def reload_theme(theme_name: str):
    """Reload COLORS and dependent style constants for a theme."""
    theme = ThemeManager.get_theme_colors(theme_name)

    COLORS.update({
        "primary": theme.get("highlight", "#1f6aa5"),
        "secondary": theme.get("highlight_dark", theme.get("highlight", "#144870")),
        "success": theme.get("success", "#2fa572"),
        "warning": theme.get("warning", "#e6a800"),
        "danger": theme.get("danger", "#d32f2f"),
        "dark": theme.get("window", "#1a1a1a"),
        "light": theme.get("window_text", "#f0f0f0"),
        "sidebar_bg": theme.get("sidebar", "#2b2b2b"),
        "content_bg": theme.get("base", "#1a1a1a"),
        "card_bg": theme.get("alternate_base", "#242424"),
        "text_primary": theme.get("window_text", "#ffffff"),
        "text_secondary": theme.get("muted_text", theme.get("window_text", "#b0b0b0")),
        "border": theme.get("border", "#3a3a3a"),
        "button_text": theme.get("button_text", theme.get("window_text", "#ffffff"))
    })


# Fonts
FONTS = {
    "title": ("Roboto", 24, "bold"),
    "heading": ("Roboto", 18, "bold"),
    "subheading": ("Roboto", 14, "bold"),
    "body": ("Roboto", 12),
    "small": ("Roboto", 10)
}

# Padding and Spacing
PADDING = {
    "small": 5,
    "medium": 10,
    "large": 20,
    "xlarge": 30
}

# Button Styles (filled with defaults then updated by reload_theme)
BUTTON_STYLES = {
    "primary": {"fg_color": "#1f6aa5", "hover_color": "#144870", "text_color": "#ffffff"},
    "secondary": {"fg_color": "#242424", "hover_color": "#3a3a3a", "text_color": "#ffffff"},
    "success": {"fg_color": "#2fa572", "hover_color": "#267d5a", "text_color": "#ffffff"},
    "danger": {"fg_color": "#d32f2f", "hover_color": "#b71c1c", "text_color": "#ffffff"}
}

# Card Style
CARD_STYLE = {"fg_color": "#242424", "corner_radius": 10, "border_width": 1, "border_color": "#3a3a3a"}

# Initialize and subscribe to theme changes
reload_theme(current_theme)
ThemeManager.subscribe(reload_theme)