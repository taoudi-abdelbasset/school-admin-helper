"""
Sidebar Navigation Component - WITH DYNAMIC TOOLS
Replace your existing ui/sidebar.py with this
"""
import customtkinter as ctk
from config.settings import SIDEBAR_WIDTH, APP_NAME
from ui.styles import COLORS, FONTS, PADDING
from core.data_manager import DataManager


class Sidebar(ctk.CTkFrame):
    """Sidebar navigation component with dynamic tools"""
    
    def __init__(self, parent, on_menu_select):
        super().__init__(
            parent,
            width=SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=COLORS["sidebar_bg"]
        )
        
        self.on_menu_select = on_menu_select
        self.current_button = None
        self.data_manager = DataManager()
        
        # Get tool manager from parent
        self.tool_manager = parent.tool_manager if hasattr(parent, 'tool_manager') else None
        
        # Prevent sidebar from shrinking
        self.grid_propagate(False)
        
        self._create_header()
        self._create_menu_items()
        self._create_tools_section()
        self._create_footer()
    
    def _create_header(self):
        """Create sidebar header"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=PADDING["large"], pady=PADDING["large"])
        
        # App name
        app_label = ctk.CTkLabel(
            header_frame,
            text=APP_NAME,
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        app_label.pack(pady=(0, PADDING["small"]))
        
        # Separator
        separator = ctk.CTkFrame(header_frame, height=2, fg_color=COLORS["border"])
        separator.pack(fill="x", pady=PADDING["medium"])
    
    def _create_menu_items(self):
        """Create main menu navigation items"""
        menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        menu_frame.pack(fill="x", padx=PADDING["medium"])
        
        # Menu items
        menu_items = [
            ("🏠 Dashboard", "dashboard"),
            ("⭐ Favorites", "favorites"),
            ("🕐 Recent", "recent"),
        ]
        
        for text, page in menu_items:
            btn = ctk.CTkButton(
                menu_frame,
                text=text,
                font=FONTS["body"],
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["primary"],
                anchor="w",
                height=40,
                command=lambda p=page: self._on_menu_click(p)
            )
            btn.pack(fill="x", pady=PADDING["small"])
            
            # Store reference
            btn.page_name = page
            
            # Set dashboard as default
            if page == "dashboard":
                self.current_button = btn
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color=COLORS["text_primary"]
                )
    
    def _create_tools_section(self):
        """Create tools section with all available tools"""
        if not self.tool_manager:
            return
        
        # Separator
        separator_frame = ctk.CTkFrame(self, fg_color="transparent")
        separator_frame.pack(fill="x", padx=PADDING["large"], pady=PADDING["medium"])
        
        separator = ctk.CTkFrame(separator_frame, height=2, fg_color=COLORS["border"])
        separator.pack(fill="x")
        
        # Tools header
        tools_header = ctk.CTkLabel(
            self,
            text="🔧 Tools",
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        tools_header.pack(fill="x", padx=PADDING["large"], pady=(PADDING["small"], PADDING["medium"]))
        
        # Scrollable tools list
        tools_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            height=300
        )
        tools_scroll.pack(fill="both", expand=True, padx=PADDING["medium"])
        
        # Get all tools
        all_tools = self.tool_manager.get_all_tools()
        favorites = self.data_manager.get_favorites()
        
        # Create tool buttons
        for tool_id, tool_info in all_tools.items():
            self._create_tool_button(tools_scroll, tool_id, tool_info, tool_id in favorites)
    
    def _create_tool_button(self, parent, tool_id, tool_info, is_favorite):
        """Create a tool button with favorite toggle"""
        # Container for tool item
        tool_container = ctk.CTkFrame(parent, fg_color="transparent")
        tool_container.pack(fill="x", pady=PADDING["small"])
        
        # Tool button
        btn = ctk.CTkButton(
            tool_container,
            text=f"{tool_info['icon']} {tool_info['name']}",
            font=FONTS["small"],
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["primary"],
            anchor="w",
            height=35,
            command=lambda: self._on_tool_click(tool_id)
        )
        btn.pack(side="left", fill="x", expand=True)
        btn.page_name = tool_id
        
        # Favorite button
        fav_btn = ctk.CTkButton(
            tool_container,
            text="⭐" if is_favorite else "☆",
            font=("Roboto", 14),
            fg_color="transparent",
            text_color=COLORS["warning"] if is_favorite else COLORS["text_secondary"],
            hover_color=COLORS["border"],
            width=30,
            height=35,
            command=lambda: self._toggle_favorite(tool_id, fav_btn)
        )
        fav_btn.pack(side="right", padx=(PADDING["small"], 0))
    
    def _toggle_favorite(self, tool_id, button):
        """Toggle favorite status"""
        favorites = self.data_manager.get_favorites()
        
        if tool_id in favorites:
            # Remove from favorites
            favorites.remove(tool_id)
            button.configure(text="☆", text_color=COLORS["text_secondary"])
        else:
            # Add to favorites
            favorites.append(tool_id)
            button.configure(text="⭐", text_color=COLORS["warning"])
        
        # Save
        data = self.data_manager.load_data()
        data["favorites"] = favorites
        self.data_manager.save_data(data)
    
    def _create_footer(self):
        """Create sidebar footer"""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=PADDING["large"], pady=PADDING["large"], side="bottom")
        
        # Separator
        separator = ctk.CTkFrame(footer_frame, height=2, fg_color=COLORS["border"])
        separator.pack(fill="x", pady=(0, PADDING["medium"]))
        
        # Settings button
        settings_btn = ctk.CTkButton(
            footer_frame,
            text="⚙️ Settings",
            font=FONTS["body"],
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["border"],
            anchor="w",
            height=35,
            command=lambda: self._on_menu_click("settings")
        )
        settings_btn.pack(fill="x")
        settings_btn.page_name = "settings"
    
    def _on_menu_click(self, page):
        """Handle menu item click"""
        self._update_button_states(page)
        self.on_menu_select(page)
    
    def _on_tool_click(self, tool_id):
        """Handle tool click"""
        # Track as recent
        self.data_manager.add_recent_tool(tool_id)
        
        # Update UI
        self._update_button_states(tool_id)
        self.on_menu_select(tool_id)
    
    def _update_button_states(self, selected_page):
        """Update button states when selection changes"""
        # Reset all buttons
        for widget in self.winfo_children():
            self._reset_buttons_in_widget(widget)
        
        # Find and highlight the selected button
        for widget in self.winfo_children():
            self._highlight_button_in_widget(widget, selected_page)
    
    def _reset_buttons_in_widget(self, widget):
        """Recursively reset buttons in a widget"""
        if isinstance(widget, ctk.CTkButton) and hasattr(widget, 'page_name'):
            widget.configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"]
            )
        
        # Check children
        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                self._reset_buttons_in_widget(child)
    
    def _highlight_button_in_widget(self, widget, page_name):
        """Recursively find and highlight the selected button"""
        if isinstance(widget, ctk.CTkButton) and hasattr(widget, 'page_name'):
            if widget.page_name == page_name:
                widget.configure(
                    fg_color=COLORS["primary"],
                    text_color=COLORS["text_primary"]
                )
                self.current_button = widget
        
        # Check children
        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                self._highlight_button_in_widget(child, page_name)