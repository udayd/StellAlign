from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFormLayout, QSlider, QComboBox, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from ui.styles import get_visibility_icon, ROW_SPACING
from ui.widgets.color_picker import InlineColorPicker
from ui.widgets.components import create_button, create_slider_row, create_divider, LineStyleSelector

class CircleTabWidget(QWidget):
    """A dynamic tab containing the settings for a single circle."""
    def __init__(self, panel, circle_index):
        super().__init__()
        self.panel = panel
        self.circle_index = circle_index
        self.main_state = panel.state
        self.circle = self.main_state.circles[circle_index]
        
        circle_main_layout = QVBoxLayout(self)
        circle_header = QHBoxLayout()
        
        self.btn_vis = create_button(
            variant='icon_round', 
            tooltip=f"Toggle {self.circle.name} Visibility", 
            checkable=True
        )
        self.btn_vis.setChecked(self.circle.visible)
        self.btn_vis.toggled.connect(self.on_vis_toggled)
        self.panel._update_visibility_button(self.btn_vis, self.circle.visible)
        
        self.btn_anchor = create_button(variant='icon_round', icon_name='crosshairs', tooltip="Set as Anchor (Move Main Crosshair Here)")
        self.btn_anchor.clicked.connect(self.on_set_anchor)
        
        self.btn_snap = create_button(variant='icon_round', icon_name='magnet', tooltip="Snap to Anchor (Move this Circle to Main Crosshair)")
        self.btn_snap.clicked.connect(self.on_snap_anchor)
        
        self.btn_center = create_button(variant='icon_round', icon_name='center-mark', tooltip="Toggle Center Mark", checkable=True)
        self.btn_center.setChecked(self.circle.center_mark_visible)
        self.btn_center.toggled.connect(self.on_center_toggled)
        
        self.btn_delete = create_button(variant='icon_round', icon_name='trash', tooltip="Delete this Circle")
        self.btn_delete.clicked.connect(self.on_delete)
        
        circle_header.addWidget(self.btn_vis)
        circle_header.addWidget(self.btn_anchor)
        circle_header.addWidget(self.btn_snap)
        circle_header.addWidget(self.btn_center)
        circle_header.addStretch()
        circle_header.addWidget(self.btn_delete)
        circle_main_layout.addLayout(circle_header)
        
        circle_layout = QFormLayout()
        circle_layout.setVerticalSpacing(ROW_SPACING)
        
        self.slider_radius = QSlider(Qt.Orientation.Horizontal)
        self.slider_radius.setRange(10, 500)
        self.slider_radius.setValue(self.circle.radius)
        self.slider_radius.valueChanged.connect(self.on_radius_changed)
        
        self.slider_offset_x = QSlider(Qt.Orientation.Horizontal)
        self.slider_offset_x.setRange(-400, 400)
        self.slider_offset_x.setValue(self.circle.offset_x)
        self.slider_offset_x.valueChanged.connect(self.on_offset_x_changed)
        
        self.slider_offset_y = QSlider(Qt.Orientation.Horizontal)
        self.slider_offset_y.setRange(-400, 400)
        self.slider_offset_y.setValue(self.circle.offset_y)
        self.slider_offset_y.valueChanged.connect(self.on_offset_y_changed)
        
        self.slider_thickness = QSlider(Qt.Orientation.Horizontal)
        self.slider_thickness.setRange(1, 10)
        self.slider_thickness.setValue(self.circle.thickness)
        self.slider_thickness.valueChanged.connect(self.on_thickness_changed)
        
        self.style_selector = LineStyleSelector(self.circle.line_style, self.on_style_changed)
        
        self.palette_color = InlineColorPicker(self.circle.color, self.on_color_changed)
        
        self.combo_mask = QComboBox()
        self.combo_mask.addItems(["None", "Mask Inside", "Mask Outside"])
        mode_map = {"none": 0, "inside": 1, "outside": 2}
        self.combo_mask.setCurrentIndex(mode_map.get(self.circle.mask_mode, 0))
        self.combo_mask.currentIndexChanged.connect(self.on_mask_changed)
        
        self.slider_mask_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_mask_opacity.setRange(10, 100)
        self.slider_mask_opacity.setValue(self.circle.mask_opacity)
        self.slider_mask_opacity.valueChanged.connect(self.on_mask_opacity_changed)
        
        circle_layout.addRow("Radius:", create_slider_row(self.slider_radius, 'minus', 'plus'))
        circle_layout.addRow("Offset X:", create_slider_row(self.slider_offset_x, 'chevron-left', 'chevron-right'))
        circle_layout.addRow("Offset Y:", create_slider_row(self.slider_offset_y, 'chevron-up', 'chevron-down'))
        circle_layout.addRow(create_divider())
        circle_layout.addRow("Thickness:", create_slider_row(self.slider_thickness, 'minus', 'plus'))
        circle_layout.addRow("Style:", self.style_selector)
        circle_layout.addRow("Color:", self.palette_color)
        circle_layout.addRow(create_divider())
        circle_layout.addRow("Mask Mode:", self.combo_mask)
        circle_layout.addRow("Mask Opacity:", create_slider_row(self.slider_mask_opacity, 'minus', 'plus'))
        
        circle_main_layout.addLayout(circle_layout)

    def on_vis_toggled(self, checked):
        self.circle.visible = checked
        self.panel._update_visibility_button(self.btn_vis, checked)
        icon = get_visibility_icon(checked, self.main_state.night_mode)
        self.panel.tabs.setTabIcon(self.circle_index + 1, icon)

    def on_set_anchor(self):
        self.main_state.crosshair_offset_x = self.circle.offset_x
        self.main_state.crosshair_offset_y = self.circle.offset_y
        self.panel.slider_crosshair_offset_x.setValue(self.circle.offset_x)
        self.panel.slider_crosshair_offset_y.setValue(self.circle.offset_y)
        self.panel.show_notification(f"Anchor Set to {self.circle.name}")

    def on_snap_anchor(self):
        self.slider_offset_x.setValue(self.main_state.crosshair_offset_x)
        self.slider_offset_y.setValue(self.main_state.crosshair_offset_y)
        self.panel.show_notification(f"{self.circle.name} Snapped to Anchor")

    def on_center_toggled(self, checked): self.circle.center_mark_visible = checked
    
    def on_delete(self):
        if len(self.main_state.circles) <= 1:
            self.panel.show_notification("Cannot delete the last circle.")
            return
        reply = QMessageBox.question(self, 'Delete Circle', 
                                     f"Are you sure you want to delete {self.circle.name}?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.main_state.circles.pop(self.circle_index)
            # Defer the UI refresh safely to the next event loop tick
            QTimer.singleShot(0, self.panel.refresh_circle_tabs)

    def on_radius_changed(self, val): self.circle.radius = val
    def on_offset_x_changed(self, val): self.circle.offset_x = val
    def on_offset_y_changed(self, val): self.circle.offset_y = val
    def on_thickness_changed(self, val): self.circle.thickness = val
    def on_color_changed(self, val): self.circle.color = val
    def on_style_changed(self, val): self.circle.line_style = val
    def on_mask_changed(self, idx):
        modes = ["none", "inside", "outside"]
        self.circle.mask_mode = modes[idx]
    def on_mask_opacity_changed(self, val): self.circle.mask_opacity = val