"""
PDF Template Editor - PyQt6 Version (WITH RESIZE & DATA NODES)
Place in: tools/pdf_generator/template_editor.py

NEW FEATURES:
✅ Resize handles like Canva
✅ Data Nodes concept (one data node = many fields)
✅ Add/delete data nodes
✅ Add multiple field instances from same data node
✅ Proper field loading with all parameters
✅ Text alignment controls
✅ Always-visible property sidebar
"""
import sys
import base64
from datetime import datetime

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsItem, QGraphicsEllipseItem, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QSpinBox, QColorDialog, QCheckBox,
    QFrame, QScrollArea, QLineEdit, QMessageBox, QInputDialog
)
from PyQt6.QtGui import (
    QPixmap, QImage, QPen, QColor, QFont, QBrush, QPainter
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal

try:
    import fitz  # PyMuPDF
except ImportError:
    print("⚠️ PyMuPDF not installed")
    fitz = None

from config.language_manager import get_language_manager  # Add this import


class ResizeHandle(QGraphicsEllipseItem):
    """Resize handle for field"""
    
    def __init__(self, parent_field, corner):
        super().__init__(-5, -5, 10, 10)
        self.parent_field = parent_field
        self.corner = corner  # "nw", "ne", "sw", "se"
        
        self.setBrush(QBrush(QColor("#2196f3")))
        self.setPen(QPen(QColor("white"), 2))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor if corner in ["nw", "se"] else Qt.CursorShape.SizeBDiagCursor)
        
        self.is_dragging = False
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.is_dragging:
            new_pos = value
            parent_rect = self.parent_field.sceneBoundingRect()
            
            # Calculate delta from initial position
            delta_x = new_pos.x() - self.initial_pos.x()
            delta_y = new_pos.y() - self.initial_pos.y()
            
            if self.corner == "se":  # Bottom-right
                new_width = max(50, self.initial_width + delta_x)
                new_height = max(20, self.initial_height + delta_y)
                self.parent_field.resize_from_handle(new_width, new_height, "x", "y")
                
            elif self.corner == "sw":  # Bottom-left
                new_width = max(50, self.initial_width - delta_x)
                new_height = max(20, self.initial_height + delta_y)
                if new_width >= 50:
                    new_x = self.initial_x + (self.initial_width - new_width)
                    self.parent_field.resize_from_handle(new_width, new_height, new_x, "y")
                    
            elif self.corner == "ne":  # Top-right
                new_width = max(50, self.initial_width + delta_x)
                new_height = max(20, self.initial_height - delta_y)
                if new_height >= 20:
                    new_y = self.initial_y + (self.initial_height - new_height)
                    self.parent_field.resize_from_handle(new_width, new_height, "x", new_y)
                    
            elif self.corner == "nw":  # Top-left
                new_width = max(50, self.initial_width - delta_x)
                new_height = max(20, self.initial_height - delta_y)
                if new_width >= 50 and new_height >= 20:
                    new_x = self.initial_x + (self.initial_width - new_width)
                    new_y = self.initial_y + (self.initial_height - new_height)
                    self.parent_field.resize_from_handle(new_width, new_height, new_x, new_y)
            
            return self.pos()  # Don't actually move the handle
            
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        self.is_dragging = True
        # Store initial values when starting drag
        self.initial_width = self.parent_field.field["width"]
        self.initial_height = self.parent_field.field["height"]
        self.initial_x = self.parent_field.field["x"]
        self.initial_y = self.parent_field.field["y"]
        self.initial_pos = self.pos()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        super().mouseReleaseEvent(event)


class FieldGraphicsItem(QGraphicsRectItem):
    """Field with resize handles and text"""
    
    def __init__(self, field_data, parent_editor):
        # Get actual coordinates from field
        actual_x = field_data["x"]
        actual_y = field_data["y"]
        actual_w = field_data.get("width", 180)
        actual_h = field_data.get("height", 36)
        
        # Scale for display if render_scale exists
        scale = getattr(parent_editor, 'render_scale', 1.0)
        display_x = actual_x * scale
        display_y = actual_y * scale
        display_w = actual_w * scale
        display_h = actual_h * scale
        
        super().__init__(0, 0, display_w, display_h)
        
        self.field = field_data
        self.parent_editor = parent_editor
        
        # Make movable and selectable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        # Set position (in display coordinates)
        self.setPos(display_x, display_y)
        
        print(f"  Creating field item:")
        print(f"    Actual coords: ({actual_x}, {actual_y}) {actual_w}x{actual_h}")
        print(f"    Display coords: ({display_x}, {display_y}) {display_w}x{display_h}")
        print(f"    Scale factor: {scale}x")
        
        # Style
        self.setPen(QPen(QColor("#9e9e9e"), 1, Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        
        # Add text item
        self.text_item = QGraphicsTextItem(field_data["data_node"], self)
        
        # Resize handles
        self.handles = {
            "nw": ResizeHandle(self, "nw"),
            "ne": ResizeHandle(self, "ne"),
            "sw": ResizeHandle(self, "sw"),
            "se": ResizeHandle(self, "se")
        }
        
        for handle in self.handles.values():
            handle.setParentItem(self)
            handle.setVisible(False)
        
        self.update_text_display()
        self.update_handles_position()
        
    def resize_from_handle(self, new_width, new_height, new_x="x", new_y="y"):
        """Resize field from handle drag - converts display to actual coords"""
        scale = getattr(self.parent_editor, 'render_scale', 1.0)
        
        # Convert display size to actual PDF size
        actual_new_width = int(new_width / scale)
        actual_new_height = int(new_height / scale)
        
        old_w = self.field["width"]
        old_h = self.field["height"]
        
        self.field["width"] = actual_new_width
        self.field["height"] = actual_new_height
        
        if new_x != "x":
            actual_new_x = int(new_x / scale)
            self.field["x"] = actual_new_x
            
        if new_y != "y":
            actual_new_y = int(new_y / scale)
            self.field["y"] = actual_new_y
        
        print(f"🔧 RESIZE: {old_w}x{old_h} → {self.field['width']}x{self.field['height']}")
        
        self.update_from_field()
        
        if self.parent_editor:
            self.parent_editor.update_properties_display()
    
    def update_handles_position(self):
        """Position handles at corners"""
        rect = self.rect()
        self.handles["nw"].setPos(0, 0)
        self.handles["ne"].setPos(rect.width(), 0)
        self.handles["sw"].setPos(0, rect.height())
        self.handles["se"].setPos(rect.width(), rect.height())
    
    def update_text_display(self):
        """Update text appearance"""
        # Font
        font = QFont(self.field.get("font_family", "Arial"))
        font.setPointSize(self.field.get("font_size", 16))
        font.setBold(self.field.get("bold", False))
        font.setItalic(self.field.get("italic", False))
        font.setUnderline(self.field.get("underline", False))
        
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(self.field.get("color", "#000000")))
        self.text_item.setPlainText(self.field["data_node"])
        
        # Alignment - use DISPLAY size for positioning
        w = self.rect().width()
        h = self.rect().height()
        text_width = self.text_item.boundingRect().width()
        text_height = self.text_item.boundingRect().height()
        
        align = self.field.get("align", "left")
        if align == "left":
            x = 8
        elif align == "center":
            x = (w - text_width) / 2
        else:  # right
            x = w - text_width - 8
        
        y = (h - text_height) / 2
        self.text_item.setPos(x, y)
    
    def update_from_field(self):
        """Update visual from field data - FIXED to respect scaling"""
        # Get actual values from field (in PDF coordinates)
        actual_w = self.field.get("width", 180)
        actual_h = self.field.get("height", 36)
        actual_x = self.field.get("x", 200)
        actual_y = self.field.get("y", 200)
        
        # Scale for display
        scale = getattr(self.parent_editor, 'render_scale', 1.0)
        display_w = actual_w * scale
        display_h = actual_h * scale
        display_x = actual_x * scale
        display_y = actual_y * scale
        
        # Update size (in display coordinates)
        self.setRect(0, 0, display_w, display_h)
        
        # Update position (in display coordinates)
        self.setPos(display_x, display_y)
        
        # Update text
        self.update_text_display()
        
        # Update handles
        self.update_handles_position()
    
    def itemChange(self, change, value):
        """Handle item changes - converts display to actual coords"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            pos = self.pos()
            
            # Convert display coordinates to actual PDF coordinates
            scale = getattr(self.parent_editor, 'render_scale', 1.0)
            actual_x = int(pos.x() / scale)
            actual_y = int(pos.y() / scale)
            
            # Store in actual PDF coordinates
            self.field["x"] = actual_x
            self.field["y"] = actual_y
            
            # Check bounds
            if hasattr(self.parent_editor, 'actual_pdf_height'):
                if actual_y > self.parent_editor.actual_pdf_height:
                    print(f"⚠️ WARNING: Field Y ({actual_y}) is below page bottom ({int(self.parent_editor.actual_pdf_height)})!")
                if actual_y < 0:
                    print(f"⚠️ WARNING: Field Y ({actual_y}) is above page top!")
            
            if self.parent_editor:
                self.parent_editor.update_properties_display()
                
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if value:  # Selected
                self.setPen(QPen(QColor("#2196f3"), 2, Qt.PenStyle.SolidLine))
                for handle in self.handles.values():
                    handle.setVisible(True)
                
                if self.parent_editor:
                    self.parent_editor.select_field(self.field)
            else:  # Deselected
                self.setPen(QPen(QColor("#9e9e9e"), 1, Qt.PenStyle.DashLine))
                for handle in self.handles.values():
                    handle.setVisible(False)
        
        return super().itemChange(change, value)


class PDFTemplateEditor(QWidget):
    """PDF Template Editor with Data Nodes concept"""
    
    backRequested = pyqtSignal()
    saveRequested = pyqtSignal(str)
    dataRequested = pyqtSignal()  # Signal to open data section

    def __init__(self, project, pdf_data_manager, parent=None):
        super().__init__(parent)
        self.project = project
        self.pdf_data_manager = pdf_data_manager
        
        # NEW: Data nodes (unique variable names)
        self.data_nodes = []  # List of unique data node names
        
        # Fields (multiple instances can share same data_node)
        self.fields = []
        self.selected_field = None
        self.field_items = {}
        
        # Graphics scene and view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setBackgroundBrush(QBrush(QColor("#2d2d2d")))
        
        self.lang_manager = get_language_manager()  # Add language manager
        
        self.setup_ui()
        self.load_pdf_background()
        self.load_fields()

    def load_pdf_background(self):
        """Load PDF as background - FIXED to use actual PDF dimensions"""
        pdf_filename = self.project.get("pdf_file_name")
        if not pdf_filename:
            return

        try:
            pdf_data = self.pdf_data_manager.load_pdf_file(self.project["id"], pdf_filename)
            if not pdf_data:
                return

            pdf_bytes = base64.b64decode(pdf_data)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]
            
            # 🔴 CRITICAL: Store the ACTUAL PDF page dimensions
            # These are the dimensions PyMuPDF will use when generating
            self.actual_pdf_width = page.rect.width
            self.actual_pdf_height = page.rect.height
            
            print("\n" + "="*70)
            print("📐 PDF DIMENSIONS (What PyMuPDF Actually Sees)")
            print("="*70)
            print(f"Actual PDF size: {self.actual_pdf_width} x {self.actual_pdf_height}")
            print("="*70 + "\n")

            # Render at 2x for better quality, but TRACK the scale factor
            self.render_scale = 2.0
            pix = page.get_pixmap(matrix=fitz.Matrix(self.render_scale, self.render_scale))
            
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)

            # Add to scene
            self.background_item = self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
            
            # Show info overlay
            self._show_dimension_info(pixmap.width(), pixmap.height())
            
            print(f"✅ PDF loaded and rendered")
            print(f"   Rendered size: {pixmap.width()}x{pixmap.height()} (at {self.render_scale}x scale)")
            print(f"   Actual PDF: {self.actual_pdf_width}x{self.actual_pdf_height}")
            print(f"\n⚠️ IMPORTANT: Field coordinates are in ACTUAL PDF units ({self.actual_pdf_width}x{self.actual_pdf_height})")
            print(f"   Display scale is {self.render_scale}x for better visibility\n")
            
        except Exception as e:
            print(f"❌ Error loading PDF: {e}")
            import traceback
            traceback.print_exc()

    def _show_dimension_info(self, display_width, display_height):
        """Show PDF dimension info on canvas"""
        from PyQt6.QtWidgets import QGraphicsTextItem
        from PyQt6.QtGui import QFont, QColor
        
        info_text = QGraphicsTextItem()
        info_text.setPlainText(
            f"📐 PDF: {int(self.actual_pdf_width)}×{int(self.actual_pdf_height)}pt\n"
            f"🖥️ Display: {display_width}×{display_height}px (@{self.render_scale}x)\n"
            f"⚠️ Keep fields within bounds!"
        )
        
        font = QFont("Arial", 12, QFont.Weight.Bold)
        info_text.setFont(font)
        info_text.setDefaultTextColor(QColor("#ff3333"))
        info_text.setPos(10, 10)
        
        # Add semi-transparent background
        from PyQt6.QtWidgets import QGraphicsRectItem
        from PyQt6.QtGui import QBrush, QPen
        
        bg = QGraphicsRectItem(5, 5, 400, 80)
        bg.setBrush(QBrush(QColor(0, 0, 0, 200)))
        bg.setPen(QPen(QColor("#ff3333"), 2))
        
        self.scene.addItem(bg)
        self.scene.addItem(info_text)

    def setup_ui(self):
        """Create UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # LEFT: Data Nodes
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)

        # CENTER: Canvas + Toolbar
        center_widget = self.create_center_panel()
        main_layout.addWidget(center_widget, 1)

        # RIGHT: Properties
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)

    def create_left_panel(self):
        """Left data nodes panel"""
        panel = QFrame()
        panel.setFixedWidth(240)
        panel.setStyleSheet("""
            QFrame {
                background-color: #242424;
                border-right: 1px solid #2d2d2d;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel(f"📊 {self.lang_manager.get('pdf_generator.data_nodes', 'Data Nodes')}")
        title.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        subtitle = QLabel(self.lang_manager.get('pdf_generator.data_nodes_desc', 'One data node = multiple fields'))
        subtitle.setStyleSheet("color: #808080; font-size: 10px; margin-bottom: 5px;")
        layout.addWidget(subtitle)
        
        # Add data node input
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)
        
        self.node_input = QLineEdit()
        self.node_input.setPlaceholderText(self.lang_manager.get('pdf_generator.node_placeholder', 'e.g., firstname'))
        self.node_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #1f6aa5;
            }
        """)
        self.node_input.returnPressed.connect(self.add_data_node)
        input_layout.addWidget(self.node_input)
        
        add_btn = QPushButton("➕")
        add_btn.setFixedSize(36, 36)
        add_btn.setStyleSheet("""
            QPushButton {
                background: #1f6aa5;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #144870;
            }
        """)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_data_node)
        input_layout.addWidget(add_btn)
        
        layout.addWidget(input_frame)
        
        # Data nodes list
        self.nodes_scroll = QScrollArea()
        self.nodes_scroll.setWidgetResizable(True)
        self.nodes_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.nodes_scroll.setStyleSheet("background: transparent;")
        
        self.nodes_widget = QWidget()
        self.nodes_layout = QVBoxLayout(self.nodes_widget)
        self.nodes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.nodes_layout.setSpacing(8)
        
        self.nodes_scroll.setWidget(self.nodes_widget)
        layout.addWidget(self.nodes_scroll)
        
        return panel

    def create_center_panel(self):
        """Center canvas panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background: #2b2b2b; border-bottom: 1px solid #3a3a3a;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        
        hint = QLabel(self.lang_manager.get('pdf_generator.drag_hint', '💡 Drag to move • Drag handles to resize'))
        hint.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        toolbar_layout.addWidget(hint)
        
        toolbar_layout.addStretch()
        
        zoom_in_btn = QPushButton(self.lang_manager.get('pdf_generator.zoom_in', '🔍+'))
        zoom_in_btn.setStyleSheet(self._get_toolbar_btn_style())
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton(self.lang_manager.get('pdf_generator.zoom_out', '🔍-'))
        zoom_out_btn.setStyleSheet(self._get_toolbar_btn_style())
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(zoom_out_btn)
        
        fit_btn = QPushButton(self.lang_manager.get('pdf_generator.zoom_fit', 'Fit'))
        fit_btn.setStyleSheet(self._get_toolbar_btn_style())
        fit_btn.clicked.connect(self.zoom_fit)
        toolbar_layout.addWidget(fit_btn)
        
        toolbar_layout.addSpacing(20)
        
        back_btn = QPushButton(f"← {self.lang_manager.get('pdf_generator.back', 'Back')}")
        back_btn.setStyleSheet("""
            QPushButton {
                background: #404040;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #505050;
            }
        """)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.backRequested.emit())
        toolbar_layout.addWidget(back_btn)
        
        save_btn = QPushButton(f"💾 {self.lang_manager.get('pdf_generator.save', 'Save')}")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #2fa572;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #267d5a;
            }
        """)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_template)
        toolbar_layout.addWidget(save_btn)
        
        # Data Table button
        data_btn = QPushButton(f"📊 {self.lang_manager.get('pdf_generator.data_table', 'Data Table')}")
        data_btn.setStyleSheet("""
            QPushButton {
                background: #6b46c1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #553c9a;
            }
        """)
        data_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        data_btn.clicked.connect(self.open_data_section)
        toolbar_layout.addWidget(data_btn)
        
        layout.addWidget(toolbar)
        layout.addWidget(self.view)
        
        return widget
    
    def _get_toolbar_btn_style(self):
        return """
            QPushButton {
                background: transparent;
                color: #e0e0e0;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #404040;
            }
        """

    def create_right_panel(self):
        """Right properties panel"""
        panel = QFrame()
        panel.setFixedWidth(280)
        panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-left: 1px solid #2d2d2d;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel(f"⚙️ {self.lang_manager.get('pdf_generator.field_properties', 'Field Properties')}")
        title.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        props_widget = QWidget()
        self.props_layout = QVBoxLayout(props_widget)
        self.props_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.props_layout.setSpacing(15)
        
        self.create_property_widgets()
        
        scroll.setWidget(props_widget)
        layout.addWidget(scroll)
        
        return panel

    def create_property_widgets(self):
        """Create property inputs"""
        # Data node name
        self.prop_data_node = QLabel("No field selected")
        self.prop_data_node.setStyleSheet("color: #2196f3; font-size: 16px; font-weight: bold;")
        self.props_layout.addWidget(self.prop_data_node)
        
        # Create container for all field properties
        self.props_container = QWidget()
        self.props_container_layout = QVBoxLayout(self.props_container)
        self.props_container_layout.setContentsMargins(0, 0, 0, 0)
        self.props_container_layout.setSpacing(15)
        
        # Dimensions
        self._add_section_label_to_container(self.lang_manager.get('pdf_generator.dimensions', 'Dimensions'))
        
        self.prop_width = QSpinBox()
        self.prop_width.setRange(50, 2000)
        self.prop_width.setPrefix(self.lang_manager.get('pdf_generator.width', 'Width') + ": ")
        self.prop_width.setSuffix(" px")
        self.prop_width.setStyleSheet(self._get_input_style())
        self.prop_width.valueChanged.connect(self.update_field_property)
        self.props_container_layout.addWidget(self.prop_width)
        
        self.prop_height = QSpinBox()
        self.prop_height.setRange(20, 2000)
        self.prop_height.setPrefix(self.lang_manager.get('pdf_generator.height', 'Height') + ": ")
        self.prop_height.setSuffix(" px")
        self.prop_height.setStyleSheet(self._get_input_style())
        self.prop_height.valueChanged.connect(self.update_field_property)
        self.props_container_layout.addWidget(self.prop_height)
        
        # Font
        self._add_section_label_to_container(self.lang_manager.get('pdf_generator.font', 'Font'))
        
        self.prop_font = QComboBox()
        self.prop_font.addItems(["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana"])
        self.prop_font.setStyleSheet(self._get_input_style())
        self.prop_font.currentTextChanged.connect(self.update_field_property)
        self.props_container_layout.addWidget(self.prop_font)
        
        self.prop_size = QSpinBox()
        self.prop_size.setRange(6, 144)
        self.prop_size.setPrefix(self.lang_manager.get('pdf_generator.font_size', 'Size') + ": ")
        self.prop_size.setSuffix(" pt")
        self.prop_size.setStyleSheet(self._get_input_style())
        self.prop_size.valueChanged.connect(self.update_field_property)
        self.props_container_layout.addWidget(self.prop_size)
        
        # Text Alignment
        self._add_section_label_to_container(self.lang_manager.get('pdf_generator.text_alignment', 'Text Alignment'))
        
        align_frame = QFrame()
        align_layout = QHBoxLayout(align_frame)
        align_layout.setContentsMargins(0, 0, 0, 0)
        align_layout.setSpacing(8)
        
        self.prop_align_left = QPushButton(self.lang_manager.get('pdf_generator.align_left', 'Left'))
        self.prop_align_center = QPushButton(self.lang_manager.get('pdf_generator.align_center', 'Center'))
        self.prop_align_right = QPushButton(self.lang_manager.get('pdf_generator.align_right', 'Right'))
        
        for btn in [self.prop_align_left, self.prop_align_center, self.prop_align_right]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #404040;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #505050;
                }
                QPushButton[selected="true"] {
                    background: #1f6aa5;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            align_layout.addWidget(btn)
        
        self.prop_align_left.clicked.connect(lambda: self.set_alignment("left"))
        self.prop_align_center.clicked.connect(lambda: self.set_alignment("center"))
        self.prop_align_right.clicked.connect(lambda: self.set_alignment("right"))
        
        self.props_container_layout.addWidget(align_frame)
        
        # Style
        self._add_section_label_to_container(self.lang_manager.get('pdf_generator.style', 'Style'))
        
        self.prop_bold = QCheckBox(self.lang_manager.get('pdf_generator.bold', 'Bold'))
        self.prop_bold.setStyleSheet("color: #e0e0e0;")
        self.prop_bold.stateChanged.connect(self.update_field_property)
        self.props_container_layout.addWidget(self.prop_bold)
        
        self.prop_italic = QCheckBox(self.lang_manager.get('pdf_generator.italic', 'Italic'))
        self.prop_italic.setStyleSheet("color: #e0e0e0;")
        self.prop_italic.stateChanged.connect(self.update_field_property)
        self.props_container_layout.addWidget(self.prop_italic)
        
        self.prop_underline = QCheckBox(self.lang_manager.get('pdf_generator.underline', 'Underline'))
        self.prop_underline.setStyleSheet("color: #e0e0e0;")
        self.prop_underline.stateChanged.connect(self.update_field_property)
        self.props_container_layout.addWidget(self.prop_underline)
        
        # Color
        self._add_section_label_to_container(self.lang_manager.get('pdf_generator.color', 'Color'))
        
        color_frame = QFrame()
        color_layout = QHBoxLayout(color_frame)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(8)
        
        self.prop_color_preview = QLabel("")
        self.prop_color_preview.setFixedSize(32, 32)
        self.prop_color_preview.setStyleSheet("background: #000000; border: 1px solid #404040; border-radius: 4px;")
        color_layout.addWidget(self.prop_color_preview)
        
        color_btn = QPushButton(self.lang_manager.get('pdf_generator.pick_color', 'Pick Color'))
        color_btn.setStyleSheet("""
            QPushButton {
                background: #404040;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #505050;
            }
        """)
        color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        color_btn.clicked.connect(self.pick_color)
        color_layout.addWidget(color_btn, 1)
        
        self.props_container_layout.addWidget(color_frame)
        
        # Delete
        self.props_container_layout.addSpacing(20)
        
        delete_btn = QPushButton(self.lang_manager.get('pdf_generator.delete_field', 'Delete Field'))
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #d32f2f;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #b71c1c;
            }
        """)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(self.delete_selected_field)
        self.props_container_layout.addWidget(delete_btn)
        
        self.props_layout.addWidget(self.props_container)
        
        # Initially show with disabled state
        self.set_properties_enabled(False)
    
    def _add_section_label_to_container(self, text):
        """Add section label to container"""
        label = QLabel(text)
        label.setStyleSheet("color: #e0e0e0; font-weight: bold; margin-top: 10px;")
        self.props_container_layout.addWidget(label)
    
    def _get_input_style(self):
        return """
            QSpinBox, QComboBox {
                padding: 6px;
                background: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                color: white;
            }
            QSpinBox:focus, QComboBox:focus {
                border: 1px solid #1f6aa5;
            }
        """
    
    def set_properties_enabled(self, enabled):
        """Enable/disable property inputs"""
        self.props_container.setEnabled(enabled)
        if not enabled:
            self.prop_data_node.setText(self.lang_manager.get('pdf_generator.no_field_selected', 'No field selected'))
            self.prop_data_node.setStyleSheet("color: #808080; font-size: 16px; font-weight: bold;")
        else:
            self.prop_data_node.setStyleSheet("color: #2196f3; font-size: 16px; font-weight: bold;")
    
    def set_alignment(self, alignment):
        """Set text alignment"""
        if not self.selected_field:
            return
        
        old_align = self.selected_field.get("align", "left")
        self.selected_field["align"] = alignment
        
        print(f"\n↔️ ALIGNMENT CHANGED: {old_align} → {alignment}\n")
        
        # Update button states
        self.prop_align_left.setProperty("selected", alignment == "left")
        self.prop_align_center.setProperty("selected", alignment == "center")
        self.prop_align_right.setProperty("selected", alignment == "right")
        
        # Refresh styles
        for btn in [self.prop_align_left, self.prop_align_center, self.prop_align_right]:
            btn.setStyle(btn.style())
        
        # Update field visual
        field_id = self.selected_field["id"]
        if field_id in self.field_items:
            self.field_items[field_id].update_from_field()

    def zoom_in(self):
        self.view.scale(1.25, 1.25)

    def zoom_out(self):
        self.view.scale(0.8, 0.8)

    def zoom_fit(self):
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def add_data_node(self):
        """Add new data node"""
        node_name = self.node_input.text().strip()
        if not node_name:
            return
        
        if node_name in self.data_nodes:
            QMessageBox.warning(self, self.lang_manager.get('pdf_generator.duplicate_node_title', 'Duplicate'), 
                                self.lang_manager.get('pdf_generator.duplicate_node_message', "Data node '{name}' already exists!").format(name=node_name))
            return
        
        self.data_nodes.append(node_name)
        self.node_input.clear()
        
        # Create first field instance for this data node
        self.add_field_instance(node_name)
        
        self.refresh_data_nodes_list()
        
        print(f"✅ Added data node: {node_name}")

    def add_field_instance(self, data_node):
        """Add field instance from data node"""
        field = {
            "id": f"f_{int(datetime.now().timestamp() * 1000)}",
            "data_node": data_node,
            "x": 200, 
            "y": 200,
            "width": 180, 
            "height": 36,
            "font_family": "Arial",
            "font_size": 16,
            "color": "#000000",
            "bold": False,
            "italic": False,
            "underline": False,
            "align": "left"
        }
        
        self.fields.append(field)
        self.add_field_to_scene(field)

    def add_field_to_scene(self, field):
        """Add field to scene"""
        item = FieldGraphicsItem(field, self)
        self.scene.addItem(item)
        self.field_items[field["id"]] = item

    def refresh_data_nodes_list(self):
        """Refresh data nodes list"""
        while self.nodes_layout.count():
            child = self.nodes_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not self.data_nodes:
            no_nodes = QLabel("No data nodes yet\nAdd one above!")
            no_nodes.setStyleSheet("color: #808080; padding: 20px;")
            no_nodes.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.nodes_layout.addWidget(no_nodes)
            return
        
        for node in self.data_nodes:
            node_card = self.create_node_card(node)
            self.nodes_layout.addWidget(node_card)
    
    def create_node_card(self, node_name):
        """Create data node card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #2d2d2d;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header with name and delete
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel(f"📌 {node_name}")
        name_label.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(name_label)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #d32f2f;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #d32f2f;
                color: white;
                border-radius: 3px;
            }
        """)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.delete_data_node(node_name))
        header_layout.addWidget(delete_btn)
        
        layout.addWidget(header)
        
        # Field count
        field_count = len([f for f in self.fields if f["data_node"] == node_name])
        count_label = QLabel(f"{field_count} field(s)")
        count_label.setStyleSheet("color: #808080; font-size: 10px;")
        layout.addWidget(count_label)
        
        # Add field button
        add_field_btn = QPushButton("+ Add Field")
        add_field_btn.setStyleSheet("""
            QPushButton {
                background: #1f6aa5;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #144870;
            }
        """)
        add_field_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_field_btn.clicked.connect(lambda: self.add_field_instance(node_name))
        layout.addWidget(add_field_btn)
        
        return card
    
    def delete_data_node(self, node_name):
        """Delete data node and all its fields"""
        field_count = len([f for f in self.fields if f["data_node"] == node_name])
        
        reply = QMessageBox.question(
            self,
            self.lang_manager.get('pdf_generator.delete_node_title', 'Delete Data Node'),
            self.lang_manager.get('pdf_generator.delete_node_message', "Delete '{name}' and its {count} field(s)?").format(name=node_name, count=field_count),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_nodes.remove(node_name)
            
            fields_to_remove = [f for f in self.fields if f["data_node"] == node_name]
            for field in fields_to_remove:
                if field["id"] in self.field_items:
                    self.scene.removeItem(self.field_items[field["id"]])
                    del self.field_items[field["id"]]
                self.fields.remove(field)
            
            self.refresh_data_nodes_list()

    def select_field(self, field):
        """Select field"""
        print("\n" + "="*60)
        print("🎯 FIELD SELECTED")
        print("="*60)
        print(f"Field ID: {field.get('id')}")
        print(f"Data Node: {field.get('data_node')}")
        print(f"Position: x={field.get('x')}, y={field.get('y')}")
        print(f"Size: {field.get('width')}x{field.get('height')}")
        print(f"Font: {field.get('font_family')} {field.get('font_size')}pt")
        print(f"Color: {field.get('color')}")
        print(f"Alignment: {field.get('align')}")
        print(f"Bold: {field.get('bold')}, Italic: {field.get('italic')}, Underline: {field.get('underline')}")
        print("="*60 + "\n")
        
        self.selected_field = field
        self.set_properties_enabled(True)
        self.update_properties_display()

    def update_properties_display(self):
        """Update properties from selected field"""
        if not self.selected_field:
            self.set_properties_enabled(False)
            return
        
        print("\n📋 UPDATING PROPERTY DISPLAY")
        print("-" * 40)
        
        f = self.selected_field
        self.prop_data_node.setText(f"Data: {f['data_node']}")
        
        width_val = int(f.get("width", 180))
        height_val = int(f.get("height", 36))
        font_val = f.get("font_family", "Arial")
        size_val = int(f.get("font_size", 16))
        bold_val = f.get("bold", False)
        italic_val = f.get("italic", False)
        underline_val = f.get("underline", False)
        align_val = f.get("align", "left")
        color_val = f.get("color", "#000000")
        
        print(f"Setting Width: {width_val}")
        print(f"Setting Height: {height_val}")
        print(f"Setting Font: {font_val}")
        print(f"Setting Size: {size_val}")
        print(f"Setting Alignment: {align_val}")
        print(f"Setting Color: {color_val}")
        print(f"Setting Bold: {bold_val}, Italic: {italic_val}, Underline: {underline_val}")
        
        self.prop_width.setValue(width_val)
        self.prop_height.setValue(height_val)
        self.prop_font.setCurrentText(font_val)
        self.prop_size.setValue(size_val)
        self.prop_bold.setChecked(bold_val)
        self.prop_italic.setChecked(italic_val)
        self.prop_underline.setChecked(underline_val)
        
        # Update alignment buttons
        self.prop_align_left.setProperty("selected", align_val == "left")
        self.prop_align_center.setProperty("selected", align_val == "center")
        self.prop_align_right.setProperty("selected", align_val == "right")
        
        for btn in [self.prop_align_left, self.prop_align_center, self.prop_align_right]:
            btn.setStyle(btn.style())
        
        # Update color preview
        self.prop_color_preview.setStyleSheet(f"background: {color_val}; border: 1px solid #404040; border-radius: 4px;")
        
        print("-" * 40 + "\n")

    def update_field_property(self):
        """Update field from properties"""
        if not self.selected_field:
            return
        
        print("\n✏️ PROPERTY CHANGED")
        print("-" * 40)
        print(f"Field: {self.selected_field.get('data_node')}")
        
        old_width = self.selected_field.get("width")
        old_height = self.selected_field.get("height")
        old_font = self.selected_field.get("font_family")
        old_size = self.selected_field.get("font_size")
        old_bold = self.selected_field.get("bold")
        old_italic = self.selected_field.get("italic")
        old_underline = self.selected_field.get("underline")
        
        self.selected_field["width"] = self.prop_width.value()
        self.selected_field["height"] = self.prop_height.value()
        self.selected_field["font_family"] = self.prop_font.currentText()
        self.selected_field["font_size"] = self.prop_size.value()
        self.selected_field["bold"] = self.prop_bold.isChecked()
        self.selected_field["italic"] = self.prop_italic.isChecked()
        self.selected_field["underline"] = self.prop_underline.isChecked()
        
        print(f"Width: {old_width} → {self.selected_field['width']}")
        print(f"Height: {old_height} → {self.selected_field['height']}")
        print(f"Font: {old_font} → {self.selected_field['font_family']}")
        print(f"Size: {old_size} → {self.selected_field['font_size']}")
        print(f"Bold: {old_bold} → {self.selected_field['bold']}")
        print(f"Italic: {old_italic} → {self.selected_field['italic']}")
        print(f"Underline: {old_underline} → {self.selected_field['underline']}")
        print("-" * 40 + "\n")
        
        field_id = self.selected_field["id"]
        if field_id in self.field_items:
            self.field_items[field_id].update_from_field()

    def pick_color(self):
        """Pick color"""
        if not self.selected_field:
            return
        
        current_color = QColor(self.selected_field.get("color", "#000000"))
        color = QColorDialog.getColor(current_color, self, "Pick Text Color")
        
        if color.isValid():
            old_color = self.selected_field.get("color", "#000000")
            self.selected_field["color"] = color.name()
            
            print(f"\n🎨 COLOR CHANGED: {old_color} → {color.name()}\n")
            
            self.prop_color_preview.setStyleSheet(f"background: {color.name()}; border: 1px solid #404040; border-radius: 4px;")
            field_id = self.selected_field["id"]
            if field_id in self.field_items:
                self.field_items[field_id].update_from_field()

    def delete_selected_field(self):
        """Delete field"""
        if not self.selected_field:
            return
        
        field_id = self.selected_field["id"]
        
        if field_id in self.field_items:
            self.scene.removeItem(self.field_items[field_id])
            del self.field_items[field_id]
        
        self.fields = [f for f in self.fields if f["id"] != field_id]
        self.selected_field = None
        self.set_properties_enabled(False)
        self.refresh_data_nodes_list()

    def load_fields(self):
        """Load existing fields - FIXED to scale coordinates"""
        config = self.pdf_data_manager.load_project_config(self.project["id"])
        self.fields = config.get("fields", [])
        self.data_nodes = list(set(f["data_node"] for f in self.fields))
        
        print("\n" + "="*60)
        print("📂 LOADING FIELDS FROM CONFIG")
        print("="*60)
        
        for i, field in enumerate(self.fields):
            print(f"\nField {i+1}: {field.get('data_node', 'unnamed')}")
            print(f"  Stored coordinates: ({field.get('x')}, {field.get('y')})")
            
            # Ensure all required properties exist with defaults
            field.setdefault("width", 180)
            field.setdefault("height", 36)
            field.setdefault("font_family", "Arial")
            field.setdefault("font_size", 16)
            field.setdefault("color", "#000000")
            field.setdefault("bold", False)
            field.setdefault("italic", False)
            field.setdefault("underline", False)
            field.setdefault("align", "left")
            field.setdefault("x", 200)
            field.setdefault("y", 200)
            
            # Check if coordinates are valid
            if hasattr(self, 'actual_pdf_height'):
                if field['y'] > self.actual_pdf_height:
                    print(f"  ⚠️ WARNING: Y position ({field['y']}) is BELOW page bottom ({int(self.actual_pdf_height)})!")
                    print(f"     This field will be INVISIBLE in generated PDFs!")
            
            self.add_field_to_scene(field)
        
        self.refresh_data_nodes_list()
        print(f"\n✅ Loaded {len(self.fields)} fields from {len(self.data_nodes)} data nodes")
        print("="*60 + "\n")
    
    def save_template(self):
        """Save template"""
        print("\n" + "="*60)
        print("💾 SAVING TEMPLATE")
        print("="*60)
        
        for i, field in enumerate(self.fields):
            print(f"\nField {i+1}: {field.get('data_node')}")
            print(f"  Position: ({field.get('x')}, {field.get('y')})")
            print(f"  Size: {field.get('width')}x{field.get('height')}")
            print(f"  Font: {field.get('font_family')} {field.get('font_size')}pt")
            print(f"  Color: {field.get('color')}")
            print(f"  Alignment: {field.get('align')}")
            print(f"  Style: Bold={field.get('bold')}, Italic={field.get('italic')}, Underline={field.get('underline')}")
        
        config = {
            "fields": self.fields,
            "data_nodes": self.data_nodes,
            "updated_at": datetime.now().isoformat()
        }
        
        success = self.pdf_data_manager.save_project_config(self.project["id"], config)
        
        if success:
            print("\n✅ Template saved successfully")
            print("="*60 + "\n")
            QMessageBox.information(self, self.lang_manager.get('pdf_generator.success', 'Success'), self.lang_manager.get('pdf_generator.template_saved', 'Template saved successfully!'))
            self.saveRequested.emit(self.project["id"])
        else:
            print("\n❌ Failed to save template")
            print("="*60 + "\n")
            QMessageBox.critical(self, self.lang_manager.get('common.error', 'Error'), self.lang_manager.get('pdf_generator.save_failed', 'Failed to save template'))

    def open_data_section(self):
        """Request to open data section"""
        # Save current state first
        config = {
            "fields": self.fields,
            "data_nodes": self.data_nodes,
            "updated_at": datetime.now().isoformat()
        }
        self.pdf_data_manager.save_project_config(self.project["id"], config)
        
        # Emit signal to parent to open data section
        self.dataRequested.emit()
        print("📊 Opening data section...")