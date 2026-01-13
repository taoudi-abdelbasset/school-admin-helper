"""
PDF Generator Tool - Main Router
Place this in: tools/pdf_generator.py
"""
from tools.base_tool import BaseTool
from core.data_manager import DataManager

# Import the project list section
# We'll create the other sections later
import sys
import os

# Add pdf_generator folder to path so we can import sections
pdf_gen_path = os.path.join(os.path.dirname(__file__), 'pdf_generator')
if pdf_gen_path not in sys.path:
    sys.path.insert(0, pdf_gen_path)

from project_list import ProjectListSection


class PDFGeneratorTool(BaseTool):
    """
    PDF Generator Tool - Main Router
    Routes between different sections: Project List, Template Editor, Data Manager
    """
    
    TOOL_NAME = "PDF Generator"
    TOOL_DESCRIPTION = "Create PDF cards from templates and CSV data"
    TOOL_CATEGORY = "Utilities"
    TOOL_ICON = "📄"
    
    def __init__(self, parent):
        self.data_manager = DataManager()
        self.current_section = None
        
        super().__init__(parent)
    
    def _create_tool_content(self):
        """Show Project List by default"""
        self.show_project_list_section()
    
    def clear_content(self):
        """Clear current section"""
        # Get the content area (between header and this is the tool content)
        for widget in self.winfo_children():
            # Skip the header frame (it's the first child from base_tool)
            if widget != self.winfo_children()[0]:
                widget.destroy()
    
    def show_project_list_section(self):
        """Show the Project List section"""
        self.clear_content()
        
        # Create and pack the project list section
        self.current_section = ProjectListSection(
            parent=self,
            data_manager=self.data_manager,
            on_open_project=self.open_template_editor
        )
        self.current_section.pack(fill="both", expand=True)
    
    def open_template_editor(self, project_id):
        """
        Open the template editor for a project
        (To be implemented in next section)
        """
        from tkinter import messagebox
        messagebox.showinfo(
            "Coming Soon",
            f"Template Editor for project {project_id}\n\nThis will be implemented in the next section!"
        )
        
        # TODO: Implement template editor section
        # self.show_template_editor_section(project_id)
    
    def show_template_editor_section(self, project_id):
        """
        Show the Template Editor section
        (To be implemented)
        """
        pass
    
    def show_data_manager_section(self, project_id):
        """
        Show the Data Manager section
        (To be implemented)
        """
        pass