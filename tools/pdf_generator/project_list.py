"""
Project List Section for PDF Generator
Place this in: tools/pdf_generator/project_list.py
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import os
import sys

# Import PDF data manager
pdf_gen_path = os.path.join(os.path.dirname(__file__))
if pdf_gen_path not in sys.path:
    sys.path.insert(0, pdf_gen_path)

from pdf_data_manager import PDFDataManager
from ui.styles import COLORS, FONTS, PADDING


class ProjectListSection(ctk.CTkFrame):
    """
    Project List Section - Manages PDF template projects
    Handles: Create, Edit, Delete, Open projects
    """
    
    def __init__(self, parent, data_manager, on_open_project):
        super().__init__(parent, fg_color="transparent")
        
        self.old_data_manager = data_manager  # Keep for app settings
        
        # Use new PDF-specific data manager
        base_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        self.pdf_data_manager = PDFDataManager(base_data_dir)
        
        self.on_open_project = on_open_project
        self.projects = []
        
        self.load_projects()
        self.create_ui()
    
    def load_projects(self):
        """Load projects from storage"""
        self.projects = self.pdf_data_manager.load_projects_list()
    
    def save_projects(self):
        """Save projects to storage (no longer needed - handled by pdf_data_manager)"""
        pass
    
    def create_ui(self):
        """Create the UI"""
        self.create_header()
        self.create_projects_area()
    
    def create_header(self):
        """Create header with title and buttons"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, PADDING["large"]))
        
        title = ctk.CTkLabel(
            header_frame,
            text="📁 PDF Template Projects",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        create_btn = ctk.CTkButton(
            header_frame,
            text="➕ New Project",
            command=self.open_create_modal,
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            width=140,
            height=36
        )
        create_btn.pack(side="right")
    
    def create_projects_area(self):
        """Create area to display projects"""
        self.projects_container = ctk.CTkFrame(self, fg_color="transparent")
        self.projects_container.pack(fill="both", expand=True)
        self.refresh_projects_display()
    
    def refresh_projects_display(self):
        """Refresh the projects display"""
        for widget in self.projects_container.winfo_children():
            widget.destroy()
        
        if not self.projects:
            self.show_empty_state()
        else:
            self.show_projects_grid()
    
    def show_empty_state(self):
        """Show empty state when no projects"""
        empty_frame = ctk.CTkFrame(
            self.projects_container,
            fg_color=COLORS["card_bg"],
            corner_radius=10
        )
        empty_frame.pack(fill="both", expand=True)
        
        content = ctk.CTkFrame(empty_frame, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        icon = ctk.CTkLabel(content, text="📭", font=("Roboto", 64))
        icon.pack(pady=(0, PADDING["medium"]))
        
        title = ctk.CTkLabel(
            content,
            text="No Projects Yet",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        title.pack(pady=PADDING["small"])
        
        subtitle = ctk.CTkLabel(
            content,
            text="Create your first PDF template project to get started",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack()
    
    def show_projects_grid(self):
        """Show grid of project cards"""
        scroll_frame = ctk.CTkScrollableFrame(
            self.projects_container,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True)
        
        for idx, project in enumerate(self.projects):
            row = idx // 3
            col = idx % 3
            
            card = self.create_project_card(scroll_frame, project)
            card.grid(
                row=row,
                column=col,
                padx=PADDING["medium"],
                pady=PADDING["medium"],
                sticky="nsew"
            )
        
        for i in range(3):
            scroll_frame.grid_columnconfigure(i, weight=1, uniform="card")
    
    def create_project_card(self, parent, project):
        """Create a single project card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card_bg"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        
        # Icon
        icon_label = ctk.CTkLabel(card, text="📄", font=("Roboto", 48))
        icon_label.pack(pady=(PADDING["large"], PADDING["small"]))
        
        # Name
        name_label = ctk.CTkLabel(
            card,
            text=project["name"],
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"]
        )
        name_label.pack(pady=(0, PADDING["small"]))
        
        # Description
        desc_text = project.get("description", "No description")
        if len(desc_text) > 50:
            desc_text = desc_text[:47] + "..."
        
        desc_label = ctk.CTkLabel(
            card,
            text=desc_text,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            wraplength=200
        )
        desc_label.pack(pady=(0, PADDING["small"]))
        
        # PDF indicator
        has_pdf = project.get("pdf_file_name") is not None
        pdf_text = f"📎 {project.get('pdf_file_name', 'No PDF')}" if has_pdf else "⚠️ No PDF uploaded"
        
        pdf_indicator = ctk.CTkLabel(
            card,
            text=pdf_text,
            font=FONTS["small"],
            text_color=COLORS["success"] if has_pdf else COLORS["warning"]
        )
        pdf_indicator.pack(pady=(0, PADDING["small"]))
        
        # Date
        date_label = ctk.CTkLabel(
            card,
            text=f"Created: {project['created_at']}",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        date_label.pack(pady=(0, PADDING["medium"]))
        
        # Buttons - Fixed alignment
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=PADDING["medium"], pady=(0, PADDING["medium"]))
        
        # Configure grid for even spacing
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=0)
        btn_frame.grid_columnconfigure(2, weight=0)
        
        open_btn = ctk.CTkButton(
            btn_frame,
            text="🎨 Design",
            command=lambda: self.on_open_project(project["id"]),
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            height=32
        )
        open_btn.grid(row=0, column=0, sticky="ew", padx=(0, PADDING["small"]))
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️",
            command=lambda: self.open_edit_modal(project),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            width=40,
            height=32
        )
        edit_btn.grid(row=0, column=1, padx=PADDING["small"])
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            command=lambda: self.confirm_delete(project),
            fg_color=COLORS["danger"],
            hover_color="#b71c1c",
            width=40,
            height=32
        )
        delete_btn.grid(row=0, column=2)
        
        return card
    
    # ========== MODAL DIALOGS ==========
    
    def open_create_modal(self):
        """Open modal to create new project"""
        modal = ProjectModal(
            self,
            title="Create New Project",
            mode="create",
            on_save=self.handle_create_project
        )
        modal.grab_set()
    
    def open_edit_modal(self, project):
        """Open modal to edit existing project"""
        modal = ProjectModal(
            self,
            title="Edit Project",
            mode="edit",
            project_data=project,
            on_save=lambda data: self.handle_edit_project(project["id"], data)
        )
        modal.grab_set()
    
    def handle_create_project(self, data):
        """Handle creating a new project"""
        project_id = f"proj_{int(datetime.now().timestamp())}"
        
        # Create project metadata (lightweight!)
        project_meta = {
            "id": project_id,
            "name": data["name"],
            "description": data["description"],
            "pdf_file_name": data.get("pdf_file_name"),
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Add to projects list
        self.pdf_data_manager.add_project_to_list(project_meta)
        
        # Create project folder
        self.pdf_data_manager.create_project_folder(project_id)
        
        # Save PDF file to project folder
        if data.get("pdf_file_data"):
            self.pdf_data_manager.save_pdf_file(
                project_id,
                data["pdf_file_data"],
                data["pdf_file_name"]
            )
        
        # Initialize config
        config = {
            "variables": [],
            "design_elements": []
        }
        self.pdf_data_manager.save_project_config(project_id, config)
        
        self.load_projects()
        self.refresh_projects_display()
        
        messagebox.showinfo("Success", f"Project '{data['name']}' created!")
    
    def handle_edit_project(self, project_id, data):
        """Handle editing an existing project"""
        # Update metadata in list
        updates = {
            "name": data["name"],
            "description": data["description"]
        }
        
        # Update PDF if new one selected
        if data.get("pdf_file_name"):
            updates["pdf_file_name"] = data["pdf_file_name"]
            self.pdf_data_manager.save_pdf_file(
                project_id,
                data["pdf_file_data"],
                data["pdf_file_name"]
            )
        
        self.pdf_data_manager.update_project_in_list(project_id, updates)
        
        self.load_projects()
        self.refresh_projects_display()
        
        messagebox.showinfo("Success", f"Project '{data['name']}' updated!")
    
    def confirm_delete(self, project):
        """Confirm and delete project"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{project['name']}'?\n\nThis action cannot be undone."
        )
        
        if result:
            # Delete completely (list + folder)
            self.pdf_data_manager.delete_project(project["id"])
            
            self.load_projects()
            self.refresh_projects_display()
            
            messagebox.showinfo("Deleted", f"Project '{project['name']}' deleted.")


# ========== SINGLE SPACIOUS MODAL ==========

class ProjectModal(ctk.CTkToplevel):
    """
    Spacious modal dialog for creating/editing projects
    """
    
    def __init__(self, parent, title, mode="create", project_data=None, on_save=None):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("550x500")
        self.resizable(False, False)
        
        self.mode = mode
        self.project_data = project_data or {}
        self.on_save = on_save
        
        self.pdf_file_path = None
        self.pdf_file_data = None
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.create_ui()
        
        if mode == "edit" and project_data:
            self.populate_fields()
        
        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self.save_project())
        self.bind("<Escape>", lambda e: self.destroy())
    
    def create_ui(self):
        """Create spacious modal UI"""
        # Main container with lots of padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        icon = "📄" if self.mode == "create" else "✏️"
        title_text = f"{icon} {self.title()}"
        
        title_label = ctk.CTkLabel(
            container,
            text=title_text,
            font=("Roboto", 24, "bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, 30))
        
        # Form in card
        form_card = ctk.CTkFrame(
            container,
            fg_color=COLORS["card_bg"],
            corner_radius=10
        )
        form_card.pack(fill="both", expand=True, pady=(0, 20))
        
        # Project Name
        name_label = ctk.CTkLabel(
            form_card,
            text="Project Name *",
            font=("Roboto", 13, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        name_label.pack(fill="x", padx=20, pady=(20, 5))
        
        self.name_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Enter project name...",
            height=40,
            font=("Roboto", 12)
        )
        self.name_entry.pack(fill="x", padx=20, pady=(0, 20))
        self.name_entry.focus()
        
        # Description
        desc_label = ctk.CTkLabel(
            form_card,
            text="Description (Optional)",
            font=("Roboto", 13, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        desc_label.pack(fill="x", padx=20, pady=(0, 5))
        
        self.desc_textbox = ctk.CTkTextbox(
            form_card,
            height=80,
            font=("Roboto", 12)
        )
        self.desc_textbox.pack(fill="x", padx=20, pady=(0, 20))
        
        # PDF File
        pdf_label = ctk.CTkLabel(
            form_card,
            text="PDF Template File *",
            font=("Roboto", 13, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        pdf_label.pack(fill="x", padx=20, pady=(0, 5))
        
        pdf_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        pdf_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.pdf_filename_label = ctk.CTkLabel(
            pdf_frame,
            text="No file selected",
            font=("Roboto", 11),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        self.pdf_filename_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        select_pdf_btn = ctk.CTkButton(
            pdf_frame,
            text="📁 Browse",
            command=self.select_pdf_file,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            height=36,
            width=120
        )
        select_pdf_btn.pack(side="right")
        
        # Buttons - Big and spacious
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["border"],
            height=45,
            font=("Roboto", 14),
            width=230
        )
        cancel_btn.pack(side="left", expand=True, padx=(0, 10))
        
        save_text = "Create Project" if self.mode == "create" else "Save Changes"
        save_btn = ctk.CTkButton(
            btn_frame,
            text=save_text,
            command=self.save_project,
            fg_color=COLORS["success"],
            hover_color="#267d5a",
            height=45,
            font=("Roboto", 14, "bold"),
            width=230
        )
        save_btn.pack(side="left", expand=True, padx=(10, 0))
    
    def populate_fields(self):
        """Populate fields when editing"""
        self.name_entry.insert(0, self.project_data.get("name", ""))
        
        desc = self.project_data.get("description", "")
        if desc:
            self.desc_textbox.insert("1.0", desc)
        
        pdf_name = self.project_data.get("pdf_file_name")
        if pdf_name:
            self.pdf_filename_label.configure(
                text=f"📎 {pdf_name}",
                text_color=COLORS["success"]
            )
    
    def select_pdf_file(self):
        """Open file dialog to select PDF"""
        file_path = filedialog.askopenfilename(
            title="Select PDF Template File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.pdf_file_path = file_path
            filename = os.path.basename(file_path)
            
            try:
                import base64
                with open(file_path, 'rb') as f:
                    self.pdf_file_data = base64.b64encode(f.read()).decode()
                
                self.pdf_filename_label.configure(
                    text=f"📎 {filename}",
                    text_color=COLORS["success"]
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read PDF: {str(e)}")
    
    def save_project(self):
        """Validate and save project"""
        name = self.name_entry.get().strip()
        description = self.desc_textbox.get("1.0", "end").strip()
        
        if not name:
            messagebox.showwarning("Required Field", "Please enter a project name")
            self.name_entry.focus()
            return
        
        if self.mode == "create" and not self.pdf_file_data:
            messagebox.showwarning("Required Field", "Please select a PDF template file")
            return
        
        data = {
            "name": name,
            "description": description
        }
        
        if self.pdf_file_data:
            data["pdf_file_name"] = os.path.basename(self.pdf_file_path)
            data["pdf_file_data"] = self.pdf_file_data
        
        if self.on_save:
            self.on_save(data)
        
        self.destroy()