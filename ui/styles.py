"""
UI Styles and Constants
"""

# Colors
COLORS = {
    "primary": "#1f6aa5",
    "secondary": "#144870",
    "success": "#2fa572",
    "warning": "#e6a800",
    "danger": "#d32f2f",
    "dark": "#1a1a1a",
    "light": "#f0f0f0",
    "sidebar_bg": "#2b2b2b",
    "content_bg": "#1a1a1a",
    "card_bg": "#242424",
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "border": "#3a3a3a"
}

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

# Button Styles
BUTTON_STYLES = {
    "primary": {
        "fg_color": COLORS["primary"],
        "hover_color": COLORS["secondary"],
        "text_color": COLORS["text_primary"]
    },
    "secondary": {
        "fg_color": COLORS["card_bg"],
        "hover_color": COLORS["border"],
        "text_color": COLORS["text_primary"]
    },
    "success": {
        "fg_color": COLORS["success"],
        "hover_color": "#267d5a",
        "text_color": COLORS["text_primary"]
    },
    "danger": {
        "fg_color": COLORS["danger"],
        "hover_color": "#b71c1c",
        "text_color": COLORS["text_primary"]
    }
}

# Card Style
CARD_STYLE = {
    "fg_color": COLORS["card_bg"],
    "corner_radius": 10,
    "border_width": 1,
    "border_color": COLORS["border"]
}