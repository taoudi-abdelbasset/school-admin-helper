"""
PDF Generation Engine - AGGRESSIVE Box Expansion with Debug
Place in: tools/pdf_generator/pdf_generator_engine.py

FIXES:
✅ Much more aggressive box expansion for large fonts
✅ Better debug output to see what's happening
✅ Validates that text will fit before inserting
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
    
    progressUpdated = pyqtSignal(int, int, str)
    generationComplete = pyqtSignal(str)
    generationError = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_cancelled = False
    
    def cancel(self):
        self.is_cancelled = True
    
    def generate_pdfs(self, project, pdf_data_manager, output_path):
        self.is_cancelled = False
        
        try:
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
            print(f"CSV rows: {len(csv_data)}")
            
            if not fields:
                raise ValueError("No fields defined in template.")
            
            if not csv_data:
                raise ValueError("No data to generate PDFs from.")
            
            # Load template PDF
            self.progressUpdated.emit(10, 100, "Loading template PDF...")
            
            pdf_filename = project.get("pdf_file_name")
            if not pdf_filename:
                raise ValueError("No template PDF found.")
            
            pdf_data = pdf_data_manager.load_pdf_file(project["id"], pdf_filename)
            if not pdf_data:
                raise ValueError("Could not load template PDF file.")
            
            pdf_bytes = base64.b64decode(pdf_data)
            template_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            print(f"\n✅ Template loaded: {template_doc[0].rect.width}x{template_doc[0].rect.height}")
            
            # Create output document
            output_doc = fitz.open()
            
            total_rows = len(csv_data)
            
            for idx, row_data in enumerate(csv_data):
                if self.is_cancelled:
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
                
                template_page = template_doc[0]
                new_page = output_doc.new_page(
                    width=template_page.rect.width,
                    height=template_page.rect.height
                )
                
                new_page.show_pdf_page(
                    new_page.rect,
                    template_doc,
                    0
                )
                
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
            print(f"{'='*70}\n")
            
        except Exception as e:
            error_msg = f"PDF Generation Error: {str(e)}"
            print(f"\n❌ {error_msg}")
            import traceback
            traceback.print_exc()
            self.generationError.emit(error_msg)
    
    def _add_fields_to_page(self, page, fields, row_data, page_num):
        """Add data fields to a page with AGGRESSIVE box expansion"""
        fields_added = 0
        
        for i, field in enumerate(fields, 1):
            data_node = field.get("data_node")
            value = row_data.get(data_node, "")
            
            print(f"\n  Field {i}: {data_node}")
            print(f"    Value: '{value}'")
            
            if not value or value == "":
                print(f"    ⚠️ SKIPPED - No value")
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
            
            # Convert color
            color_rgb = self._hex_to_rgb(color)
            font_name = self._get_pymupdf_font(font_family, bold, italic)
            
            # 🔴 AGGRESSIVE BOX EXPANSION
            adjusted_x, adjusted_y, adjusted_width, adjusted_height = self._calculate_aggressive_box(
                page, value, font_name, font_size,
                original_x, original_y, original_width, original_height,
                align
            )
            
            if adjusted_width != original_width or adjusted_height != original_height:
                print(f"    📏 Box EXPANDED:")
                print(f"       Size: {original_width}x{original_height} → {adjusted_width}x{adjusted_height}")
                print(f"       Position: ({original_x}, {original_y}) → ({adjusted_x}, {adjusted_y})")
            
            # Alignment
            if align == "center":
                alignment = fitz.TEXT_ALIGN_CENTER
            elif align == "right":
                alignment = fitz.TEXT_ALIGN_RIGHT
            else:
                alignment = fitz.TEXT_ALIGN_LEFT
            
            rect = fitz.Rect(adjusted_x, adjusted_y, adjusted_x + adjusted_width, adjusted_y + adjusted_height)
            
            # Validate bounds
            page_rect = page.rect
            if (adjusted_x < 0 or adjusted_y < 0 or 
                adjusted_x + adjusted_width > page_rect.width or 
                adjusted_y + adjusted_height > page_rect.height):
                print(f"    ⚠️ WARNING - Field extends outside page!")
                print(f"       Page: {page_rect.width}x{page_rect.height}")
                print(f"       Field: ({adjusted_x}, {adjusted_y}) to ({adjusted_x + adjusted_width}, {adjusted_y + adjusted_height})")
            
            # Insert text
            try:
                result = page.insert_textbox(
                    rect,
                    str(value),
                    fontname=font_name,
                    fontsize=font_size,
                    color=color_rgb,
                    align=alignment
                )
                
                if result >= 0:
                    print(f"    ✅ TEXT INSERTED successfully (result={result})")
                    fields_added += 1
                else:
                    print(f"    ❌ TEXT FAILED TO FIT (result={result})")
                    print(f"       Box: {adjusted_width}x{adjusted_height}")
                    print(f"       Font: {font_size}pt")
                    print(f"       This means the box is STILL too small even after expansion!")
                    
                    # Try one more time with MASSIVE expansion
                    massive_width = max(adjusted_width * 3, 600)
                    massive_height = max(adjusted_height * 3, 200)
                    massive_rect = fitz.Rect(adjusted_x, adjusted_y, adjusted_x + massive_width, adjusted_y + massive_height)
                    
                    print(f"    🚨 RETRY with MASSIVE box: {massive_width}x{massive_height}")
                    
                    retry_result = page.insert_textbox(
                        massive_rect,
                        str(value),
                        fontname=font_name,
                        fontsize=font_size,
                        color=color_rgb,
                        align=alignment
                    )
                    
                    if retry_result >= 0:
                        print(f"    ✅ SUCCESS with massive box!")
                        fields_added += 1
                    else:
                        print(f"    ❌ STILL FAILED - Something is very wrong!")
                    
            except Exception as e:
                print(f"    ❌ ERROR inserting text: {e}")
        
        return fields_added
    
    def _calculate_aggressive_box(self, page, text, font_name, font_size, x, y, width, height, align):
        """
        Calculate box with AGGRESSIVE expansion for large fonts
        """
        # 🔴 MUCH more aggressive estimates for large fonts
        # Character width: 0.6 for normal, up to 0.75 for large fonts
        char_width_factor = min(0.75, 0.6 + (font_size / 500))
        avg_char_width = font_size * char_width_factor
        
        # Estimate text width
        text_length = len(str(text))
        estimated_text_width = text_length * avg_char_width
        
        # Line height: 1.5x font size (more generous)
        estimated_text_height = font_size * 1.5
        
        # GENEROUS padding
        padding_x = max(20, font_size * 0.5)
        padding_y = max(15, font_size * 0.4)
        
        min_width = estimated_text_width + padding_x
        min_height = estimated_text_height + padding_y
        
        # Expand if needed
        new_width = max(width, min_width)
        new_height = max(height, min_height)
        
        # 🔴 FOR LARGE FONTS: Add extra safety margin
        if font_size > 50:
            new_width = int(new_width * 1.3)  # 30% extra
            new_height = int(new_height * 1.3)
            print(f"    🔴 Large font detected ({font_size}pt) - adding 30% safety margin")
        
        # Calculate position adjustment
        new_x = x
        new_y = y
        
        if new_width > width:
            width_increase = new_width - width
            if align == "right":
                new_x = x - width_increase
            elif align == "center":
                new_x = x - (width_increase / 2)
        
        if new_height > height:
            height_increase = new_height - height
            new_y = y - (height_increase / 2)
        
        return int(new_x), int(new_y), int(new_width), int(new_height)
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b)
    
    def _get_pymupdf_font(self, font_family, bold, italic):
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
        return family_fonts.get((bold, italic), "helv")