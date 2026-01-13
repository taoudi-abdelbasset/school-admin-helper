"""
Main Application Window - WITH DYNAMIC TOOL LOADING
Replace your existing core/app.py with this
"""

from ui.styles import PADDING
import customtkinter as ctk
from config.settings import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
    APPEARANCE_MODE, COLOR_THEME
)
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.styles import COLORS
from core.tool_manager import get_tool_manager


class ToolsHelperApp(ctk.CTk):
    """Main application window with dynamic tool loading"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Set theme
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Initialize tool manager (automatically discovers all tools!)
        self.tool_manager = get_tool_manager()
        print(f"\n🎉 Loaded {len(self.tool_manager.tools)} tools automatically!\n")
        
        # Create UI components
        self._create_sidebar()
        self._create_content_area()
        
        # Show dashboard by default
        self.show_page("dashboard")
    
    def _create_sidebar(self):
        """Create sidebar navigation"""
        self.sidebar = Sidebar(self, on_menu_select=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
    
    def _create_content_area(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["content_bg"],
            corner_radius=0
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
    
    def show_page(self, page_name):
        """Show a specific page - now with automatic tool detection!"""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Check if it's a tool (automatic!)
        if page_name in self.tool_manager.tools:
            tool_instance = self.tool_manager.create_tool_instance(page_name, self.content_frame)
            if tool_instance:
                tool_instance.grid(row=0, column=0, sticky="nsew")
                return
        
        # Built-in pages
        if page_name == "dashboard":
            page = Dashboard(self.content_frame, self.tool_manager)
            page.grid(row=0, column=0, sticky="nsew")
        
        elif page_name == "favorites":
            self._show_placeholder("⭐ Favorites", "Your favorite tools will appear here")
        
        elif page_name == "recent":
            self._show_placeholder("🕐 Recent Tools", "Recently used tools will appear here")
        
        elif page_name == "all_tools":
            self._show_all_tools()
        
        elif page_name == "settings":
            self._show_placeholder("⚙️ Settings", "Application settings will be available here")
        
        else:
            self._show_placeholder("Page Not Found", f"The page '{page_name}' is not available yet")
    
    def _show_all_tools(self):
        """Show all tools page - automatically populated!"""
        all_tools_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["content_bg"]
        )
        all_tools_frame.grid(row=0, column=0, sticky="nsew")
        
        # Header
        header = ctk.CTkLabel(
            all_tools_frame,
            text="🔧 All Tools",
            font=("Roboto", 28, "bold"),
            text_color=COLORS["text_primary"]
        )
        header.pack(pady=PADDING["large"])
        
        # Group by category
        categories = self.tool_manager.get_categories()
        
        for category in categories:
            # Category header
            cat_label = ctk.CTkLabel(
                all_tools_frame,
                text=f"📁 {category}",
                font=("Roboto", 20, "bold"),
                text_color=COLORS["text_primary"],
                anchor="w"
            )
            cat_label.pack(fill="x", padx=PADDING["large"], pady=(PADDING["large"], PADDING["small"]))
            
            # Tools in this category
            tools = self.tool_manager.get_tools_by_category(category)
            
            tools_container = ctk.CTkFrame(all_tools_frame, fg_color="transparent")
            tools_container.pack(fill="x", padx=PADDING["large"], pady=PADDING["small"])
            
            for tool_id, tool_info in tools.items():
                tool_card = self._create_tool_card(tools_container, tool_id, tool_info)
                tool_card.pack(fill="x", pady=PADDING["small"])
    
    def _create_tool_card(self, parent, tool_id, tool_info):
        """Create a tool card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=10)
        
        # Left side - icon and info
        left_frame = ctk.CTkFrame(card, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=PADDING["medium"], pady=PADDING["medium"])
        
        # Icon and name
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(anchor="w")
        
        title = ctk.CTkLabel(
            title_frame,
            text=f"{tool_info['icon']} {tool_info['name']}",
            font=("Roboto", 16, "bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Description
        desc = ctk.CTkLabel(
            left_frame,
            text=tool_info['description'],
            font=("Roboto", 12),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        desc.pack(anchor="w", pady=(PADDING["small"], 0))
        
        # Right side - open button
        open_btn = ctk.CTkButton(
            card,
            text="Open",
            command=lambda: self.show_page(tool_id),
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            width=100
        )
        open_btn.pack(side="right", padx=PADDING["medium"], pady=PADDING["medium"])
        
        return card
    
    def _show_placeholder(self, title, message):
        """Show a placeholder page"""
        placeholder_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["content_bg"]
        )
        placeholder_frame.grid(row=0, column=0, sticky="nsew")
        
        # Center the content
        placeholder_frame.grid_rowconfigure(0, weight=1)
        placeholder_frame.grid_columnconfigure(0, weight=1)
        
        content = ctk.CTkFrame(placeholder_frame, fg_color="transparent")
        content.grid(row=0, column=0)
        
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=("Roboto", 32, "bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, 20))
        
        message_label = ctk.CTkLabel(
            content,
            text=message,
            font=("Roboto", 16),
            text_color=COLORS["text_secondary"]
        )
        message_label.pack()
    
    def run(self):
        """Start the application"""
        self.mainloop()


# Add missing import