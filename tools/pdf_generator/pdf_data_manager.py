"""
PDF Generator Data Manager
Place this in: tools/pdf_generator/pdf_data_manager.py

Handles separate data storage for PDF Generator:
- projects.json (lightweight project list)
- Individual project folders with their own data
"""
import json
import os
from datetime import datetime


class PDFDataManager:
    """Manages PDF Generator data with separate storage"""
    
    def __init__(self, base_data_dir):
        """
        Initialize PDF data manager
        
        Args:
            base_data_dir: The main data directory (e.g., data/)
        """
        # Setup paths
        self.base_dir = base_data_dir
        self.pdf_data_dir = os.path.join(base_data_dir, "pdf_generator")
        self.projects_file = os.path.join(self.pdf_data_dir, "projects.json")
        self.projects_folder = os.path.join(self.pdf_data_dir, "projects")
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.pdf_data_dir, exist_ok=True)
        os.makedirs(self.projects_folder, exist_ok=True)
        
        # Create projects.json if it doesn't exist
        if not os.path.exists(self.projects_file):
            self._save_projects_list([])
    
    # ========== PROJECTS LIST (Lightweight) ==========
    
    def load_projects_list(self):
        """
        Load lightweight projects list
        Returns: List of project metadata (no heavy data)
        """
        try:
            with open(self.projects_file, 'r') as f:
                data = json.load(f)
                return data.get("projects", [])
        except Exception as e:
            print(f"Error loading projects list: {e}")
            return []
    
    def _save_projects_list(self, projects):
        """Save projects list to projects.json"""
        try:
            data = {
                "projects": projects,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.projects_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving projects list: {e}")
            return False
    
    def add_project_to_list(self, project_metadata):
        """
        Add project to the list (only metadata, no heavy data)
        
        Args:
            project_metadata: Dict with id, name, description, created_at, pdf_file_name
        """
        projects = self.load_projects_list()
        projects.append(project_metadata)
        return self._save_projects_list(projects)
    
    def update_project_in_list(self, project_id, updates):
        """
        Update project metadata in list
        
        Args:
            project_id: Project ID
            updates: Dict of fields to update
        """
        projects = self.load_projects_list()
        
        for project in projects:
            if project["id"] == project_id:
                project.update(updates)
                return self._save_projects_list(projects)
        
        return False
    
    def remove_project_from_list(self, project_id):
        """Remove project from list"""
        projects = self.load_projects_list()
        projects = [p for p in projects if p["id"] != project_id]
        return self._save_projects_list(projects)
    
    # ========== INDIVIDUAL PROJECT DATA ==========
    
    def get_project_folder(self, project_id):
        """Get path to project's folder"""
        return os.path.join(self.projects_folder, project_id)
    
    def create_project_folder(self, project_id):
        """Create folder for a project"""
        project_folder = self.get_project_folder(project_id)
        os.makedirs(project_folder, exist_ok=True)
        return project_folder
    
    def save_project_config(self, project_id, config_data):
        """
        Save project configuration to its folder
        
        Args:
            project_id: Project ID
            config_data: Dict with variables, design_elements, etc.
        """
        project_folder = self.create_project_folder(project_id)
        config_file = os.path.join(project_folder, "config.json")
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving project config: {e}")
            return False
    
    def load_project_config(self, project_id):
        """
        Load project configuration from its folder
        
        Returns: Dict with project config or empty dict
        """
        project_folder = self.get_project_folder(project_id)
        config_file = os.path.join(project_folder, "config.json")
        
        if not os.path.exists(config_file):
            return {}
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading project config: {e}")
            return {}
    
    def save_pdf_file(self, project_id, pdf_data, filename):
        """
        Save PDF file to project folder
        
        Args:
            project_id: Project ID
            pdf_data: Base64 encoded PDF data
            filename: Original filename
        """
        project_folder = self.create_project_folder(project_id)
        pdf_file = os.path.join(project_folder, filename)
        
        try:
            import base64
            with open(pdf_file, 'wb') as f:
                f.write(base64.b64decode(pdf_data))
            return True
        except Exception as e:
            print(f"Error saving PDF file: {e}")
            return False
    
    def load_pdf_file(self, project_id, filename):
        """
        Load PDF file from project folder
        
        Returns: Base64 encoded PDF data or None
        """
        project_folder = self.get_project_folder(project_id)
        pdf_file = os.path.join(project_folder, filename)
        
        if not os.path.exists(pdf_file):
            return None
        
        try:
            import base64
            with open(pdf_file, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except Exception as e:
            print(f"Error loading PDF file: {e}")
            return None
    
    def save_csv_data(self, project_id, csv_data):
        """
        Save CSV data to project folder
        
        Args:
            project_id: Project ID
            csv_data: List of dicts (CSV rows)
        """
        project_folder = self.create_project_folder(project_id)
        csv_file = os.path.join(project_folder, "data.json")
        
        try:
            with open(csv_file, 'w') as f:
                json.dump({"data": csv_data}, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving CSV data: {e}")
            return False
    
    def load_csv_data(self, project_id):
        """
        Load CSV data from project folder
        
        Returns: List of dicts or empty list
        """
        project_folder = self.get_project_folder(project_id)
        csv_file = os.path.join(project_folder, "data.json")
        
        if not os.path.exists(csv_file):
            return []
        
        try:
            with open(csv_file, 'r') as f:
                data = json.load(f)
                return data.get("data", [])
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return []
    
    def delete_project(self, project_id):
        """
        Delete project completely (from list and folder)
        
        Args:
            project_id: Project ID
        """
        # Remove from list
        self.remove_project_from_list(project_id)
        
        # Delete project folder
        project_folder = self.get_project_folder(project_id)
        
        if os.path.exists(project_folder):
            try:
                import shutil
                shutil.rmtree(project_folder)
                return True
            except Exception as e:
                print(f"Error deleting project folder: {e}")
                return False
        
        return True
    
    def get_project_full_data(self, project_id):
        """
        Load complete project data (when needed)
        
        Returns: Dict with all project data
        """
        # Get metadata from list
        projects = self.load_projects_list()
        project_meta = next((p for p in projects if p["id"] == project_id), None)
        
        if not project_meta:
            return None
        
        # Load config
        config = self.load_project_config(project_id)
        
        # Load CSV data
        csv_data = self.load_csv_data(project_id)
        
        # Combine everything
        full_data = {**project_meta, **config}
        full_data["csv_data"] = csv_data
        
        return full_data