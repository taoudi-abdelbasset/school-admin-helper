"""
Theme-aware StyleSheet Generator
Generates stylesheets dynamically based on current theme
"""
from config.theme_manager import ThemeManager


def get_global_stylesheet(theme_name="dark"):
    """Generate global stylesheet for the application based on theme"""
    theme = ThemeManager.get_theme_colors(theme_name)
    
    # Extract colors from theme
    window_bg = theme.get("window", "#1a1a1a")
    window_text = theme.get("window_text", "#ffffff")
    base = theme.get("base", "#242424")
    alternate_base = theme.get("alternate_base", "#2b2b2b")
    button = theme.get("button", "#2b2b2b")
    button_text = theme.get("button_text", "#ffffff")
    highlight = theme.get("highlight", "#1f6aa5")
    highlighted_text = theme.get("highlighted_text", button_text)
    border = theme.get("border", "#3a3a3a")
    
    # Build stylesheet
    stylesheet = f"""
        * {{
            background-color: {window_bg};
            color: {window_text};
        }}
        
        QMainWindow {{
            background-color: {window_bg};
            color: {window_text};
        }}
        
        QWidget {{
            background-color: {window_bg};
            color: {window_text};
        }}
        
        QFrame {{
            background-color: {window_bg};
            color: {window_text};
        }}
        
        QLabel {{
            background-color: transparent;
            color: {window_text};
        }}
        
        QPushButton {{
            background-color: {button};
            color: {button_text};
            border: 1px solid {border};
            padding: 5px 10px;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: {highlight};
            color: {highlighted_text};
        }}
        
        QPushButton:pressed {{
            background-color: {highlight};
        }}
        
        QLineEdit {{
            background-color: {base};
            color: {window_text};
            border: 1px solid {border};
            padding: 5px;
            border-radius: 4px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {highlight};
        }}
        
        QComboBox {{
            background-color: {base};
            color: {window_text};
            border: 1px solid {border};
            padding: 5px;
            border-radius: 4px;
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {base};
            color: {window_text};
            border: 1px solid {border};
        }}
        
        QTextEdit {{
            background-color: {base};
            color: {window_text};
            border: 1px solid {border};
            padding: 5px;
            border-radius: 4px;
        }}
        
        QTableWidget {{
            background-color: {window_bg};
            color: {window_text};
            border: 1px solid {border};
            gridline-color: {border};
        }}
        
        QTableWidget::item {{
            padding: 5px;
        }}
        
        QTableWidget::item:selected {{
            background-color: {highlight};
        }}
        
        QHeaderView::section {{
            background-color: {button};
            color: {button_text};
            border: 1px solid {border};
            padding: 5px;
        }}
        
        QScrollBar:vertical {{
            background-color: {window_bg};
            border: 1px solid {border};
            width: 12px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {button};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {highlight};
        }}
        
        QScrollBar:horizontal {{
            background-color: {window_bg};
            border: 1px solid {border};
            height: 12px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {button};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {highlight};
        }}
        
        QDialog {{
            background-color: {window_bg};
            color: {window_text};
        }}
        
        QMessageBox {{
            background-color: {window_bg};
            color: {window_text};
        }}
    """
    
    return stylesheet
