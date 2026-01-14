"""
PDF Generator Tool - PyQt6 Version
Place this in: tools/pdf_generator.py

FIXED: Import issues resolved with debugging
"""
from tools.base_tool_pyqt6 import BaseToolPyQt6
from core.data_manager import DataManager
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QMessageBox
import sys
import os

# Add pdf_generator folder to path FIRST before any imports
pdf_gen_path = os.path.join(os.path.dirname(__file__), 'pdf_generator')
if pdf_gen_path not in sys.path:
    sys.path.insert(0, pdf_gen_path)

# Now import from the pdf_generator folder
from pdf_data_manager import PDFDataManager
from template_editor import PDFTemplateEditor
from data_section_pyqt6 import DataSectionPyQt6

# Import project list - delayed to avoid circular imports
def get_project_list_class():
    """Lazy import to avoid circular dependencies"""
    try:
        from project_list_pyqt6 import ProjectListSectionPyQt6
        return ProjectListSectionPyQt6
    except ImportError as e:
        print(f"❌ Import error: {e}")
        # Try to see what's actually in the module
        import project_list_pyqt6
        import inspect
        
        print("\n🔍 Available classes in project_list_pyqt6:")
        for name, obj in inspect.getmembers(project_list_pyqt6):
            if inspect.isclass(obj):
                print(f"  - {name}")
        
        # Try to find any class with "Project" in the name
        for name, obj in inspect.getmembers(project_list_pyqt6):
            if inspect.isclass(obj) and 'Project' in name:
                print(f"✅ Using class: {name}")
                return obj
        
        raise ImportError(f"Could not find ProjectListSectionPyQt6 or similar class in project_list_pyqt6.py")


class PDFGeneratorTool(BaseToolPyQt6):
    """
    PDF Generator Tool - PyQt6 Native
    No more process conflicts!
    """
    
    TOOL_NAME = "PDF Generator"
    TOOL_DESCRIPTION = "Create PDF cards from templates and CSV data"
    TOOL_CATEGORY = "Utilities"
    TOOL_ICON = "📄"
    
    def __init__(self, parent=None):
        self.data_manager = DataManager()
        
        # Initialize PDF-specific data manager
        base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.pdf_data_manager = PDFDataManager(base_data_dir)
        
        self.current_widget = None
        self.template_editor = None
        
        super().__init__(parent)
    
    def _create_tool_content(self):
        """Create content area with stack"""
        # Content container
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stack for switching views
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        
        # Show project list
        self.show_project_list()
        
        self.main_layout.addWidget(content_widget)
    
    def show_project_list(self):
        """Show project list view"""
        # Clear stack
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        
        # Get the class dynamically
        ProjectListSectionPyQt6 = get_project_list_class()
        
        # Add project list
        project_list = ProjectListSectionPyQt6(
            data_manager=self.data_manager,
            pdf_data_manager=self.pdf_data_manager,
            on_open_project=self.open_template_editor
        )
        
        self.stack.addWidget(project_list)
    
    def open_template_editor(self, project_id):
        """Open template editor (same process, no conflicts!)"""
        projects = self.pdf_data_manager.load_projects_list()
        project = next((p for p in projects if p["id"] == project_id), None)
        
        if not project:
            print("❌ Project not found")
            return
        
        # Store current project
        self.current_project = project
        
        # Clear stack
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        
        # Create template editor
        self.template_editor = PDFTemplateEditor(
            project=project,
            pdf_data_manager=self.pdf_data_manager
        )
        
        # Connect signals
        self.template_editor.backRequested.connect(self.show_project_list)
        self.template_editor.saveRequested.connect(self.on_template_saved)
        self.template_editor.dataRequested.connect(self.open_data_section)
        
        # Add to stack
        self.stack.addWidget(self.template_editor)
        
        print(f"✅ Opened template editor for: {project['name']}")
    
    def open_data_section(self):
        """Open data section"""
        if not hasattr(self, 'current_project'):
            print("❌ No current project")
            return
        
        # Clear stack
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        
        # Create data section
        data_section = DataSectionPyQt6(
            project=self.current_project,
            pdf_data_manager=self.pdf_data_manager
        )
        
        # Connect signals
        data_section.backRequested.connect(lambda: self.open_template_editor(self.current_project["id"]))
        data_section.generatePDFRequested.connect(self.generate_pdf)
        
        # Add to stack
        self.stack.addWidget(data_section)
        
        print(f"✅ Opened data section for: {self.current_project['name']}")
    
    def generate_pdf(self):
        """Generate P`DF from current data"""
        if not self.csv_data:
            QMessageBox.warning(
                self, 
                self.lang_manager.get('common.error', 'Error'),
                self.lang_manager.get('pdf_generator.no_data_generate', 'No data to generate PDFs from.\n\nPlease add some data rows first!')
            )
            return
        
        # Get output file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{self.project['name']}_output_{timestamp}.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.lang_manager.get('pdf_generator.save_generated_pdf', 'Save Generated PDF'),
            default_name,
            "PDF files (*.pdf)"
        )
        
        if not file_path:
            return
        
        # Create engine and show progress dialog
        engine = PDFGeneratorEngine()
        
        dialog = PDFGenerationDialog(
            engine,
            self.project,
            self.pdf_data_manager,
            file_path,
            parent=self
        )
        
        result = dialog.exec()
        
        if dialog.is_complete:
            reply = QMessageBox.information(
                self,
                self.lang_manager.get('pdf_generator.success', 'Success'),
                self.lang_manager.get(
                    'pdf_generator.pdf_generated',
                    f'Successfully generated {len(self.csv_data)} PDF pages!\n\nSaved to:\n{file_path}\n\nWould you like to open the file?'
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Open file with default PDF viewer
                try:
                    import subprocess
                    import platform
                    
                    if platform.system() == 'Windows':
                        os.startfile(file_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', file_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', file_path])
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        self.lang_manager.get('common.error', 'Error'),
                        f"{self.lang_manager.get('pdf_generator.open_failed', 'Could not open PDF')}:\n{str(e)}"
                    )
    
    def on_template_saved(self, project_id):
        """Handle template save"""
        print(f"✅ Template saved for project: {project_id}")