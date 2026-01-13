"""
Application Settings and Configuration
"""
import os

# Application Info
APP_NAME = "Tools Helper"
APP_VERSION = "1.0.0"
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"

# Window Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 600

# Colors (CustomTkinter themes)
APPEARANCE_MODE = "dark"  # "dark", "light", "system"
COLOR_THEME = "blue"  # "blue", "green", "dark-blue"

# Sidebar Settings
SIDEBAR_WIDTH = 250
SIDEBAR_BG_COLOR = "#2b2b2b"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")

# Data Files
DATA_FILE = os.path.join(DATA_DIR, "app_data.json")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)

# Tool Categories
TOOL_CATEGORIES = [
    "All Tools",
    "Calculators",
    "Converters",
    "Utilities",
    "Other"
]