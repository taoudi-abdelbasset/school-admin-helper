"""
Base Tool Class - Template for creating new tools
"""
import customtkinter as ctk
from ui.styles import COLORS, FONTS, PADDING


class BaseTool(ctk.CTkFrame):
    """
    Base class for all tools
    Inherit from this class when creating new tools
    """
    
    # Tool metadata (override in child classes)
    TOOL_NAME = "Base Tool"
    TOOL_DESCRIPTION = "Base tool description"
    TOOL_CATEGORY = "Other"
    TOOL_ICON = "🔧"
    
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["content_bg"],
            corner_radius=0
        )
        
        self._create_header()
        self._create_tool_content()
    
    def _create_header(self):
        """Create tool header with title and description"""
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"])
        header_frame.pack(fill="x", padx=PADDING["large"], pady=PADDING["large"])
        
        # Title with icon
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=PADDING["large"], pady=PADDING["medium"])
        
        title = ctk.CTkLabel(
            title_frame,
            text=f"{self.TOOL_ICON} {self.TOOL_NAME}",
            font=FONTS["title"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        title.pack(side="left")
        
        # Description
        if self.TOOL_DESCRIPTION:
            desc = ctk.CTkLabel(
                header_frame,
                text=self.TOOL_DESCRIPTION,
                font=FONTS["body"],
                text_color=COLORS["text_secondary"],
                anchor="w"
            )
            desc.pack(fill="x", padx=PADDING["large"], pady=(0, PADDING["medium"]))
    
    def _create_tool_content(self):
        """
        Override this method in child classes to create tool-specific content
        """
        # Placeholder content
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=PADDING["large"], pady=PADDING["large"])
        
        placeholder = ctk.CTkLabel(
            content_frame,
            text="Tool content goes here.\nOverride _create_tool_content() method to add your tool's interface.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center"
        )
        placeholder.pack(expand=True)
    
    def on_open(self):
        """
        Called when tool is opened
        Override to perform initialization
        """
        pass
    
    def on_close(self):
        """
        Called when tool is closed
        Override to perform cleanup
        """
        pass
    
    def save_state(self):
        """
        Save tool state to local storage
        Override to implement state saving
        """
        pass
    
    def load_state(self):
        """
        Load tool state from local storage
        Override to implement state loading
        """
        pass