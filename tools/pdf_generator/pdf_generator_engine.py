"""
PDF Generation Engine - Smart Box Expansion (No Font Shrinking!)
Place in: tools/pdf_generator/pdf_generator_engine.py

NEW APPROACH:
✅ Keep font size as set by user (no auto-shrinking!)
✅ Auto-expand box width/height to fit text
✅ Adjust position based on alignment to keep text in same visual spot
"""
import os
import base64
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import fitz  # PyMuPDF
except ImportError:
    print("⚠️ PyMuPDF not installed. Run: pip install PyMuPDF")
    fitz = None


class PDFGeneratorEngine(QObject):
    """Engine for generating PDFs from template + data"""
    
    # Signals for progress reporting
    progressUpdated = pyqtSignal(int, int, str)  # current, total, message
    generationComplete = pyqtSignal(str)  # output_path
    generationError = pyqtSignal(str)  # error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_cancelled = False
    
    def cancel(self):
        """Cancel generation"""
        self.is_cancelled = True
    
    def generate_pdfs(self, project, pdf_data_manager, output_path):
        """
        Generate PDFs from template and data
        
        Args:
            project: Project data with id, name, etc.
            pdf_data_manager: PDFDataManager instance
            output_path: Where to save the output PDF
        """
        self.is_cancelled = False
        
        try:
            # Load project data
            self.progressUpdated.emit(0, 100, "Loading project data...")
            
            config = pdf_data_manager.load_project_config(project["id"])
            fields = config.get("fields", [])
            data_nodes = config.get("data_nodes", [])
            csv_data = pdf_data_manager.load_csv_data(project["id"])
            
            print("\n" + "="*70)
            print("🚀 STARTING PDF GENERATION")
            print("="*70)
            print(f"Project: {project.get('name')}")
            print(f"Fields defined: {len(fields)}")
            print(f"Data nodes: {data_nodes}")
            print(f"CSV rows: {len(csv_data)}")
            
            if not fields:
                raise ValueError("No fields defined in template. Please add fields first.")
            
            if not csv_data:
                raise ValueError("No data to generate PDFs from. Please add data rows first.")
            
            # Print field details
            print("\n📋 FIELDS CONFIGURATION:")
            for i, field in enumerate(fields, 1):
                print(f"\nField {i}:")
                print(f"  Data Node: {field.get('data_node')}")
                print(f"  Position: ({field.get('x')}, {field.get('y')})")
                print(f"  Size: {field.get('width')}x{field.get('height')}")
                print(f"  Font: {field.get('font_family')} {field.get('font_size')}pt")
                print(f"  Align: {field.get('align')}")
            
            # Print sample data
            print("\n📊 SAMPLE DATA (First Row):")
            if csv_data:
                for key, value in csv_data[0].items():
                    print(f"  {key}: {value}")
            
            # Load template PDF
            self.progressUpdated.emit(10, 100, "Loading template PDF...")
            
            pdf_filename = project.get("pdf_file_name")
            if not pdf_filename:
                raise ValueError("No template PDF found for this project.")
            
            pdf_data = pdf_data_manager.load_pdf_file(project["id"], pdf_filename)
            if not pdf_data:
                raise ValueError("Could not load template PDF file.")
            
            pdf_bytes = base64.b64decode(pdf_data)
            template_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            print(f"\n✅ Template loaded: {template_doc[0].rect.width}x{template_doc[0].rect.height}")
            
            # Create output document
            output_doc = fitz.open()
            
            # Generate one page per data row
            total_rows = len(csv_data)
            
            for idx, row_data in enumerate(csv_data):
                if self.is_cancelled:
                    self.progressUpdated.emit(idx, total_rows, "Cancelled by user")
                    return
                
                progress = int(10 + (idx / total_rows) * 80)
                self.progressUpdated.emit(
                    progress, 
                    100, 
                    f"Generating page {idx + 1} of {total_rows}..."
                )
                
                print(f"\n{'='*70}")
                print(f"📄 GENERATING PAGE {idx + 1}/{total_rows}")
                print(f"{'='*70}")
                
                # Create new page from template
                template_page = template_doc[0]
                new_page = output_doc.new_page(
                    width=template_page.rect.width,
                    height=template_page.rect.height
                )
                
                # Copy template content to new page
                new_page.show_pdf_page(
                    new_page.rect,
                    template_doc,
                    0
                )
                
                print(f"✅ Template copied to page {idx + 1}")
                
                # Add data fields
                fields_added = self._add_fields_to_page(new_page, fields, row_data, idx + 1)
                print(f"✅ Added {fields_added} fields to page {idx + 1}")
            
            # Save output
            self.progressUpdated.emit(90, 100, "Saving PDF...")
            output_doc.save(output_path)
            output_doc.close()
            template_doc.close()
            
            self.progressUpdated.emit(100, 100, "Complete!")
            self.generationComplete.emit(output_path)
            
            print(f"\n{'='*70}")
            print(f"✅ GENERATION COMPLETE!")
            print(f"{'='*70}")
            print(f"Generated {total_rows} pages successfully!")
            print(f"Output: {output_path}")
            print(f"{'='*70}\n")
            
        except Exception as e:
            error_msg = f"PDF Generation Error: {str(e)}"
            print(f"\n❌ {error_msg}")
            import traceback
            traceback.print_exc()
            self.generationError.emit(error_msg)
    
    def _add_fields_to_page(self, page, fields, row_data, page_num):
        """Add data fields to a page with smart box expansion"""
        fields_added = 0
        
        for i, field in enumerate(fields, 1):
            data_node = field.get("data_node")
            value = row_data.get(data_node, "")
            
            print(f"\n  Field {i}: {data_node}")
            print(f"    Value from data: '{value}'")
            
            if not value or value == "":
                print(f"    ⚠️ SKIPPED - No value for '{data_node}'")
                continue
            
            # Get field properties
            original_x = field.get("x", 0)
            original_y = field.get("y", 0)
            original_width = field.get("width", 180)
            original_height = field.get("height", 36)
            
            font_family = field.get("font_family", "Arial")
            font_size = field.get("font_size", 16)
            color = field.get("color", "#000000")
            bold = field.get("bold", False)
            italic = field.get("italic", False)
            align = field.get("align", "left")
            
            print(f"    Original box: ({original_x}, {original_y}) {original_width}x{original_height}")
            print(f"    Font: {font_family} {font_size}pt, Align: {align}")
            
            # Convert color hex to RGB tuple
            color_rgb = self._hex_to_rgb(color)
            
            # Map font family to PyMuPDF font
            font_name = self._get_pymupdf_font(font_family, bold, italic)
            
            # 🆕 SMART BOX EXPANSION
            adjusted_x, adjusted_y, adjusted_width, adjusted_height = self._calculate_expanded_box(
                page, value, font_name, font_size,
                original_x, original_y, original_width, original_height,
                align
            )
            
            if adjusted_width != original_width or adjusted_height != original_height:
                print(f"    📏 Box expanded: {original_width}x{original_height} → {adjusted_width}x{adjusted_height}")
                if adjusted_x != original_x or adjusted_y != original_y:
                    print(f"    📍 Position adjusted: ({original_x}, {original_y}) → ({adjusted_x}, {adjusted_y})")
            
            # Determine alignment value
            if align == "center":
                alignment = fitz.TEXT_ALIGN_CENTER
            elif align == "right":
                alignment = fitz.TEXT_ALIGN_RIGHT
            else:
                alignment = fitz.TEXT_ALIGN_LEFT
            
            # Create the adjusted rectangle
            rect = fitz.Rect(adjusted_x, adjusted_y, adjusted_x + adjusted_width, adjusted_y + adjusted_height)
            
            # Check if field is within page bounds
            page_rect = page.rect
            if adjusted_x < 0 or adjusted_y < 0 or adjusted_x + adjusted_width > page_rect.width or adjusted_y + adjusted_height > page_rect.height:
                print(f"    ⚠️ WARNING - Field extends outside page bounds!")
                print(f"       Page size: {page_rect.width}x{page_rect.height}")
                print(f"       Field bounds: ({adjusted_x}, {adjusted_y}) to ({adjusted_x + adjusted_width}, {adjusted_y + adjusted_height})")
            
            # Insert text with expanded box
            try:
                result = page.insert_textbox(
                    rect,
                    str(value),
                    fontname=font_name,
                    fontsize=font_size,  # Keep original font size!
                    color=color_rgb,
                    align=alignment
                )
                
                if result >= 0:
                    print(f"    ✅ INSERTED at {font_size}pt (kept original size!) - result={result}")
                    fields_added += 1
                else:
                    print(f"    ⚠️ Failed even with expanded box - result={result}")
                    print(f"       This shouldn't happen - box might be TOO small initially")
                    
            except Exception as e:
                print(f"    ❌ ERROR inserting text: {e}")
        
        return fields_added
    
    def _calculate_expanded_box(self, page, text, font_name, font_size, x, y, width, height, align):
        """
        Calculate expanded box dimensions to fit text
        Adjusts position based on alignment to keep text in same visual spot
        """
        # Estimate text dimensions
        # PyMuPDF doesn't have a built-in way to measure text perfectly,
        # so we use approximations
        
        # Character width estimation (varies by font, but this is a good average)
        avg_char_width = font_size * 0.6  # Rough estimate for most fonts
        estimated_text_width = len(str(text)) * avg_char_width
        
        # Line height is roughly 1.2x font size
        estimated_text_height = font_size * 1.3
        
        # Add padding
        padding_x = 10
        padding_y = 8
        
        min_width = estimated_text_width + padding_x
        min_height = estimated_text_height + padding_y
        
        # Determine if we need to expand
        new_width = max(width, min_width)
        new_height = max(height, min_height)
        
        # Calculate position adjustment based on alignment
        new_x = x
        new_y = y
        
        # Width expansion based on horizontal alignment
        if new_width > width:
            width_increase = new_width - width
            
            if align == "right":
                # Text is right-aligned, expand to the LEFT
                new_x = x - width_increase
            elif align == "center":
                # Text is centered, expand BOTH sides
                new_x = x - (width_increase / 2)
            # else: align == "left", expand to the RIGHT (no x change needed)
        
        # Height expansion (always centered vertically)
        if new_height > height:
            height_increase = new_height - height
            # Expand both TOP and BOTTOM (keep text centered vertically)
            new_y = y - (height_increase / 2)
        
        return int(new_x), int(new_y), int(new_width), int(new_height)
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b)
    
    def _get_pymupdf_font(self, font_family, bold, italic):
        """Map font family to PyMuPDF font name"""
        
        font_map = {
            "Arial": {
                (False, False): "helv",
                (True, False): "hebo",
                (False, True): "heit",
                (True, True): "hebi"
            },
            "Helvetica": {
                (False, False): "helv",
                (True, False): "hebo",
                (False, True): "heit",
                (True, True): "hebi"
            },
            "Times New Roman": {
                (False, False): "times-roman",
                (True, False): "times-bold",
                (False, True): "times-italic",
                (True, True): "times-bold-italic"
            },
            "Courier New": {
                (False, False): "courier",
                (True, False): "courier-bold",
                (False, True): "courier-oblique",
                (True, True): "courier-boldoblique"
            },
            "Verdana": {
                (False, False): "helv",
                (True, False): "hebo",
                (False, True): "heit",
                (True, True): "hebi"
            }
        }
        
        family_fonts = font_map.get(font_family, font_map["Arial"])
        font_name = family_fonts.get((bold, italic), "helv")
        
        return font_name