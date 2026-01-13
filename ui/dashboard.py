"""
Dashboard Page Component - FIXED
Replace your existing ui/dashboard.py with this
"""
import customtkinter as ctk
from ui.styles import COLORS, FONTS, PADDING, CARD_STYLE
from core.data_manager import DataManager


class Dashboard(ctk.CTkScrollableFrame):
    """Dashboard page with overview and quick actions"""
    
    def __init__(self, parent, tool_manager):
        super().__init__(
            parent,
            fg_color=COLORS["content_bg"],
            corner_radius=0
        )
        
        self.tool_manager = tool_manager
        self.data_manager = DataManager()
        
        # Get reference to main app
        self.app = self._get_app()
        
        self._create_welcome_section()
        self._create_recent_tools()  # Show only recent tools
        self._create_statistics()
    
    def _get_app(self):
        """Get reference to main app window"""
        widget = self.master
        while widget:
            if hasattr(widget, 'show_page'):
                return widget
            widget = widget.master
        return None
    
    def _create_welcome_section(self):
        """Create welcome banner"""
        welcome_frame = ctk.CTkFrame(self, **CARD_STYLE)
        welcome_frame.pack(fill="x", padx=PADDING["large"], pady=PADDING["large"])
        
        title = ctk.CTkLabel(
            welcome_frame,
            text="Welcome to Tools Helper! 👋",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        )
        title.pack(pady=(PADDING["large"], PADDING["small"]), padx=PADDING["large"])
        
        subtitle = ctk.CTkLabel(
            welcome_frame,
            text="Your all-in-one toolkit for productivity",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack(pady=(0, PADDING["large"]), padx=PADDING["large"])
    
    def _create_recent_tools(self):
        """Show ONLY last 3 used tools"""
        section_frame = ctk.CTkFrame(self, fg_color="transparent")
        section_frame.pack(fill="x", padx=PADDING["large"], pady=PADDING["medium"])
        
        # Section title
        title = ctk.CTkLabel(
            section_frame,
            text="Recent Tools",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        title.pack(fill="x", pady=(0, PADDING["medium"]))
        
        # Recent tools list
        recent_frame = ctk.CTkFrame(section_frame, **CARD_STYLE)
        recent_frame.pack(fill="x")
        
        recent_tool_ids = self.data_manager.get_recent_tools()
        
        if recent_tool_ids:
            # Show only last 3
            for tool_id in recent_tool_ids[:3]:
                tool_info = self.tool_manager.get_tool(tool_id)
                
                if tool_info:
                    tool_item = ctk.CTkFrame(recent_frame, fg_color="transparent")
                    tool_item.pack(fill="x", padx=PADDING["medium"], pady=PADDING["small"])
                    
                    # Icon + Name
                    ctk.CTkLabel(
                        tool_item,
                        text=f"{tool_info['icon']} {tool_info['name']}",
                        font=FONTS["body"],
                        text_color=COLORS["text_primary"],
                        anchor="w"
                    ).pack(side="left", fill="x", expand=True)
                    
                    # Open button
                    ctk.CTkButton(
                        tool_item,
                        text="Open",
                        width=60,
                        height=25,
                        font=FONTS["small"],
                        fg_color=COLORS["primary"],
                        hover_color=COLORS["secondary"],
                        command=lambda tid=tool_id: self._open_tool(tid)
                    ).pack(side="right")
        else:
            no_tools_label = ctk.CTkLabel(
                recent_frame,
                text="No recent tools. Browse tools from sidebar!",
                font=FONTS["body"],
                text_color=COLORS["text_secondary"]
            )
            no_tools_label.pack(pady=PADDING["large"])
    
    def _open_tool(self, tool_id):
        """Open a tool and track it"""
        if self.app:
            # Track as recent
            self.data_manager.add_recent_tool(tool_id)
            # Open tool
            self.app.show_page(tool_id)
    
    def _create_statistics(self):
        """Create statistics section"""
        section_frame = ctk.CTkFrame(self, fg_color="transparent")
        section_frame.pack(fill="x", padx=PADDING["large"], pady=PADDING["medium"])
        
        # Section title
        title = ctk.CTkLabel(
            section_frame,
            text="Statistics",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        title.pack(fill="x", pady=(0, PADDING["medium"]))
        
        # Stats grid
        stats_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        stats_frame.pack(fill="x")
        
        # Configure grid
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1, uniform="stat")
        
        # Stats
        favorites_count = len(self.data_manager.get_favorites())
        recent_count = len(self.data_manager.get_recent_tools())
        total_tools = len(self.tool_manager.get_all_tools())
        
        stats = [
            ("Total Tools", str(total_tools), "📦"),
            ("Favorites", str(favorites_count), "⭐"),
            ("Recently Used", str(recent_count), "🕐")
        ]
        
        for idx, (label, value, icon) in enumerate(stats):
            stat_card = self._create_stat_card(stats_frame, label, value, icon)
            stat_card.grid(row=0, column=idx, padx=PADDING["medium"], pady=PADDING["small"], sticky="ew")
    
    def _create_stat_card(self, parent, label, value, icon):
        """Create a single statistic card"""
        card = ctk.CTkFrame(parent, **CARD_STYLE)
        
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=("Roboto", 32),
            text_color=COLORS["text_primary"]
        )
        icon_label.pack(pady=(PADDING["large"], PADDING["small"]))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Roboto", 28, "bold"),
            text_color=COLORS["primary"]
        )
        value_label.pack()
        
        label_label = ctk.CTkLabel(
            card,
            text=label,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        label_label.pack(pady=(0, PADDING["large"]))
        
        return card
    
    def refresh(self):
        """Refresh dashboard data"""
        for widget in self.winfo_children():
            widget.destroy()
        
        self._create_welcome_section()
        self._create_recent_tools()
        self._create_statistics()