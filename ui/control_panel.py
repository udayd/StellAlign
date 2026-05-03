from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QFormLayout, QPushButton, QComboBox, QLabel, QTabWidget, QSizePolicy, QMessageBox, QButtonGroup, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from core.state import CollimationState, CircleState
from ui.styles import get_visibility_icon, PANEL_WIDTH, MAX_PANEL_WIDTH, GROUP_SPACING, ROW_SPACING, SECTION_MARGINS
from ui.wizard import GuidedWizard
from ui.help_dialog import HelpDialog
from ui.settings_dialog import GlobalSettingsDialog
from ui.widgets.color_picker import InlineColorPicker
from ui.widgets.circle_tab import CircleTabWidget
from ui.widgets.components import create_button
from ui.widgets.workspace import WorkspaceWidget
from ui.widgets.notification import NotificationWidget

class ControlPanel(QWidget):
    def __init__(self, state: CollimationState, hud=None):
        super().__init__()
        self.state = state
        scaled_width = int(PANEL_WIDTH * (self.state.ui_scale / 100.0))
        scaled_max_width = int(MAX_PANEL_WIDTH * (self.state.ui_scale / 100.0))
        self.setMinimumWidth(scaled_width)
        self.setMaximumWidth(scaled_max_width)
        self.hud = hud
        self.settings_dialog = GlobalSettingsDialog(self.state, self)
        
        layout = QVBoxLayout()
        layout.setSpacing(GROUP_SPACING) # Add breathing room between major groups
        self.setLayout(layout)
        
        # --- Mode Selection ---
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(4) # Tighten the spacing between buttons
        self.btn_manual = create_button(variant='toggle_text', text="Manual", checkable=True)
        self.btn_manual.setChecked(True)
        self.btn_manual.clicked.connect(self.on_mode_manual)
        
        self.btn_wizard = create_button(variant='toggle_text', text="Assistant", checkable=True)
        self.btn_wizard.clicked.connect(self.on_mode_wizard)
        
        self.btn_settings = create_button(
            variant='icon_round', 
            icon_name='settings', 
            tooltip="Global Settings"
        )
        self.btn_settings.clicked.connect(self.show_settings)
        
        self.btn_night = create_button(
            variant='icon_round', 
            icon_name='moon', 
            tooltip="Toggle Night Vision Mode", 
            checkable=True
        )
        self.btn_night.clicked.connect(self.on_night_mode_toggled)
        
        self.btn_help = create_button(variant='icon_round', icon_name='help', tooltip="Collimation Cheatsheet")
        self.btn_help.clicked.connect(self.show_help)
        
        mode_layout.addWidget(self.btn_manual)
        mode_layout.addWidget(self.btn_wizard)
        mode_layout.addStretch()
        mode_layout.addWidget(self.btn_settings)
        mode_layout.addWidget(self.btn_night)
        mode_layout.addWidget(self.btn_help)
        layout.addLayout(mode_layout)
        
        # --- Guided Wizard Header ---
        self.wizard_widget = GuidedWizard(self.state, self)
        layout.addWidget(self.wizard_widget)
        self.wizard_widget.hide()
        
        # --- Overlay Tabs ---
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        tab_crosshair = QWidget()
        crosshair_main_layout = QVBoxLayout(tab_crosshair)
        
        crosshair_header = QHBoxLayout()
        self.btn_crosshair_vis = create_button(
            variant='icon_round', 
            tooltip="Toggle Crosshair Visibility", 
            checkable=True
        )
        self.btn_crosshair_vis.setChecked(self.state.crosshair_visible)
        self.btn_crosshair_vis.toggled.connect(self.on_crosshair_toggled)
        self._update_visibility_button(self.btn_crosshair_vis, self.state.crosshair_visible)
        
        self.btn_crosshair_reset = create_button(variant='icon_round', icon_name='redo', tooltip="Reset Offsets to Zero")
        self.btn_crosshair_reset.clicked.connect(self.on_crosshair_reset)
        
        crosshair_header.addWidget(self.btn_crosshair_vis)
        crosshair_header.addStretch()
        crosshair_header.addWidget(self.btn_crosshair_reset)
        crosshair_main_layout.addLayout(crosshair_header)
        
        crosshair_layout = QFormLayout()
        crosshair_layout.setVerticalSpacing(ROW_SPACING) # Add vertical padding to the rows
        self.slider_crosshair_offset_x = QSlider(Qt.Orientation.Horizontal)
        self.slider_crosshair_offset_x.setRange(-400, 400)
        self.slider_crosshair_offset_x.setValue(self.state.crosshair_offset_x)
        self.slider_crosshair_offset_x.valueChanged.connect(self.on_crosshair_offset_x_changed)
        
        self.slider_crosshair_offset_y = QSlider(Qt.Orientation.Horizontal)
        self.slider_crosshair_offset_y.setRange(-400, 400)
        self.slider_crosshair_offset_y.setValue(self.state.crosshair_offset_y)
        self.slider_crosshair_offset_y.valueChanged.connect(self.on_crosshair_offset_y_changed)
        
        self.slider_crosshair_thickness = QSlider(Qt.Orientation.Horizontal)
        self.slider_crosshair_thickness.setRange(1, 10)
        self.slider_crosshair_thickness.setValue(self.state.crosshair_thickness)
        self.slider_crosshair_thickness.valueChanged.connect(self.on_crosshair_thickness_changed)
        
        self.slider_crosshair_rotation = QSlider(Qt.Orientation.Horizontal)
        self.slider_crosshair_rotation.setRange(-180, 180)
        self.slider_crosshair_rotation.setValue(self.state.crosshair_rotation)
        self.slider_crosshair_rotation.valueChanged.connect(self.on_crosshair_rotation_changed)
        
        # Create Style buttons
        self.style_button_group_crosshair = QButtonGroup(self)
        self.style_button_group_crosshair.setExclusive(True)
        
        style_widget_crosshair = QWidget()
        style_layout_crosshair = QHBoxLayout(style_widget_crosshair)
        style_layout_crosshair.setContentsMargins(0,0,0,0)
        style_layout_crosshair.setSpacing(4)
        
        self.btn_solid_crosshair = create_button(variant='default', icon_name='solid', tooltip="Solid Line", checkable=True)
        self.btn_solid_crosshair.clicked.connect(lambda: self.on_crosshair_style_changed("Solid"))
        self.btn_dashed_crosshair = create_button(variant='default', icon_name='dashed', tooltip="Dashed Line", checkable=True)
        self.btn_dashed_crosshair.clicked.connect(lambda: self.on_crosshair_style_changed("Dashed"))
        self.btn_dotted_crosshair = create_button(variant='default', icon_name='dotted', tooltip="Dotted Line", checkable=True)
        self.btn_dotted_crosshair.clicked.connect(lambda: self.on_crosshair_style_changed("Dotted"))
        
        self.style_button_group_crosshair.addButton(self.btn_solid_crosshair)
        self.style_button_group_crosshair.addButton(self.btn_dashed_crosshair)
        self.style_button_group_crosshair.addButton(self.btn_dotted_crosshair)
        
        style_layout_crosshair.addWidget(self.btn_solid_crosshair)
        style_layout_crosshair.addWidget(self.btn_dashed_crosshair)
        style_layout_crosshair.addWidget(self.btn_dotted_crosshair)
        style_layout_crosshair.addStretch()

        if self.state.crosshair_line_style == "Solid": self.btn_solid_crosshair.setChecked(True)
        elif self.state.crosshair_line_style == "Dashed": self.btn_dashed_crosshair.setChecked(True)
        else: self.btn_dotted_crosshair.setChecked(True)
        
        self.palette_crosshair_color = InlineColorPicker(self.state.crosshair_color, self.on_crosshair_color_changed)
        
        crosshair_layout.addRow("Offset X:", self._create_slider_row(self.slider_crosshair_offset_x, 'chevron-left', 'chevron-right'))
        crosshair_layout.addRow("Offset Y:", self._create_slider_row(self.slider_crosshair_offset_y, 'chevron-up', 'chevron-down'))
        crosshair_layout.addRow("Thickness:", self._create_slider_row(self.slider_crosshair_thickness, 'minus', 'plus'))
        crosshair_layout.addRow("Rotation:", self._create_slider_row(self.slider_crosshair_rotation, 'undo', 'redo', True))
        crosshair_layout.addRow(self._create_divider())
        crosshair_layout.addRow("Style:", style_widget_crosshair)
        crosshair_layout.addRow("Color:", self.palette_crosshair_color)
        
        crosshair_main_layout.addLayout(crosshair_layout)
        
        crosshair_main_layout.addStretch()
        self.btn_reset_all = create_button(variant='default', text=" Reset All Overlays", icon_name='trash')
        self.btn_reset_all.clicked.connect(self.on_reset_all_overlays)
        crosshair_main_layout.addWidget(self.btn_reset_all)
        
        crosshair_icon = get_visibility_icon(self.state.crosshair_visible, self.state.night_mode)
        self.tabs.addTab(tab_crosshair, crosshair_icon, "Crosshair")
        
        # Initialize Dynamic Circle Tabs
        self.circle_tabs = []
        self.refresh_circle_tabs()
        
        self.btn_add_circle = create_button(variant='icon_flat', icon_name='plus', tooltip="Add New Circle")
        self.btn_add_circle.clicked.connect(self.on_add_circle)
        self.tabs.setCornerWidget(self.btn_add_circle, Qt.Corner.TopRightCorner)
        
        layout.addWidget(self.tabs)

        # --- Workspace Group (Profiles & Capture) ---
        self.workspace_widget = WorkspaceWidget(self, self.state)
        layout.addWidget(self.workspace_widget)
        
        layout.addStretch()
        
        # --- Notification Area ---
        self.notification = NotificationWidget()
        layout.addWidget(self.notification)
        
    def _create_slider_row(self, slider, dec_icon, inc_icon, show_value=False, auto_toggle=None):
        """Helper method to wrap a slider with decrement and increment buttons."""
        widget = QWidget()
        row = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)
        
        if auto_toggle:
            row.addWidget(auto_toggle)
            
        btn_dec = create_button(variant='icon_round', icon_name=dec_icon, auto_repeat=True)
        btn_dec.clicked.connect(lambda checked, s=slider, st=-1: s.setValue(s.value() + st))
        row.addWidget(btn_dec)
        
        row.addWidget(slider)
        
        btn_inc = create_button(variant='icon_round', icon_name=inc_icon, auto_repeat=True)
        btn_inc.clicked.connect(lambda checked, s=slider, st=1: s.setValue(s.value() + st))
        row.addWidget(btn_inc)
        
        if show_value:
            val_label = QLabel(str(slider.value()))
            val_label.setMinimumWidth(30)
            val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            slider.valueChanged.connect(lambda v, l=val_label: l.setText(str(v)))
            row.addWidget(val_label)
            
        def _update_state(*args):
            is_auto = auto_toggle.isChecked() if auto_toggle else False
            slider.setEnabled(not is_auto)
            
            can_dec = not is_auto and slider.value() > slider.minimum()
            can_inc = not is_auto and slider.value() < slider.maximum()
            
            btn_dec.setEnabled(can_dec)
            btn_inc.setEnabled(can_inc)
            
            dec_suffix = "" if can_dec else "-disabled"
            inc_suffix = "" if can_inc else "-disabled"
            
            btn_dec.setIcon(QIcon(f'assets/icons/{dec_icon}{dec_suffix}.svg'))
            btn_inc.setIcon(QIcon(f'assets/icons/{inc_icon}{inc_suffix}.svg'))
            
        slider.valueChanged.connect(_update_state)
        if auto_toggle:
            auto_toggle.toggled.connect(_update_state)
            
        _update_state()
        return widget

    def _create_divider(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 6, 12, 6) # Left, Top, Right, Bottom padding
        line = QFrame()
        line.setObjectName("section_divider")
        line.setFixedHeight(1)
        layout.addWidget(line)
        return container

    def _update_visibility_button(self, btn, is_visible):
        btn.setIcon(get_visibility_icon(is_visible, self.state.night_mode))
        btn.setStyleSheet("border-radius: 16px;")

    def on_add_circle(self):
        new_name = f"Circle {len(self.state.circles) + 1}"
        # Determine the next high contrast color to use
        next_color = InlineColorPicker.COLORS[len(self.state.circles) % len(InlineColorPicker.COLORS)]
        self.state.circles.append(CircleState(name=new_name, color=next_color))
        self.refresh_circle_tabs()
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        
    def refresh_circle_tabs(self):
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
        self.circle_tabs.clear()
        for i, circle in enumerate(self.state.circles):
            tab = CircleTabWidget(self, i)
            self.circle_tabs.append(tab)
            icon = get_visibility_icon(circle.visible, self.state.night_mode)
            self.tabs.addTab(tab, icon, circle.name)

    def on_mode_manual(self):
        self.btn_manual.setChecked(True)
        self.btn_wizard.setChecked(False)
        self.wizard_widget.hide()
        self.wizard_widget.stop_wizard()

    def on_mode_wizard(self):
        self.btn_wizard.setChecked(True)
        self.btn_manual.setChecked(False)
        self.wizard_widget.show()
        
    def show_help(self):
        dialog = HelpDialog(self)
        dialog.exec()
        
    def show_settings(self):
        self.settings_dialog.exec()
        
    def apply_accessibility_settings(self):
        scaled_width = int(PANEL_WIDTH * (self.state.ui_scale / 100.0))
        scaled_max_width = int(MAX_PANEL_WIDTH * (self.state.ui_scale / 100.0))
        self.setMinimumWidth(scaled_width)
        self.setMaximumWidth(scaled_max_width)
        
        if self.hud:
            self.hud.setFixedWidth(int(344 * (self.state.ui_scale / 100.0)))
            
        safe_palette = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#FFFFFF"]
        neon_palette = ["#00E5FF", "#FF007F", "#FFFF00", "#FF3D00", "#39FF14", "#FFFFFF"]
        
        target_palette = safe_palette if self.state.color_blind_palette else neon_palette
        if target_palette != InlineColorPicker.COLORS:
            # Swap the colors currently active on the UI
            def swap_color(cur_color):
                if cur_color.upper() in InlineColorPicker.COLORS:
                    return target_palette[InlineColorPicker.COLORS.index(cur_color.upper())]
                return cur_color
                
            self.state.crosshair_color = swap_color(self.state.crosshair_color)
            for circle in self.state.circles:
                circle.color = swap_color(circle.color)
                
        InlineColorPicker.COLORS = target_palette
        self.palette_crosshair_color.build_palette()
        self.palette_crosshair_color.set_color(self.state.crosshair_color)
        for tab in self.circle_tabs:
            tab.palette_color.build_palette()
            tab.palette_color.set_color(tab.circle.color)
        
    def on_night_mode_toggled(self, checked):
        self.state.night_mode = checked
        from ui.styles import apply_application_theme
        apply_application_theme(self.state)
        
        self._update_visibility_button(self.btn_crosshair_vis, self.state.crosshair_visible)
        self.tabs.setTabIcon(0, get_visibility_icon(self.state.crosshair_visible, self.state.night_mode))
        for i, tab in enumerate(self.circle_tabs):
            self._update_visibility_button(tab.btn_vis, tab.circle.visible)
            self.tabs.setTabIcon(i + 1, get_visibility_icon(tab.circle.visible, self.state.night_mode))

    def on_crosshair_toggled(self, checked): 
        self.state.crosshair_visible = checked
        icon = get_visibility_icon(checked, self.state.night_mode)
        self.tabs.setTabIcon(0, icon)
        self._update_visibility_button(self.btn_crosshair_vis, checked)
        
    def on_crosshair_reset(self):
        self.slider_crosshair_offset_x.setValue(0)
        self.slider_crosshair_offset_y.setValue(0)
        self.slider_crosshair_rotation.setValue(0)
        
    def on_crosshair_offset_x_changed(self, value): self.state.crosshair_offset_x = value
    def on_crosshair_offset_y_changed(self, value): self.state.crosshair_offset_y = value
    def on_crosshair_thickness_changed(self, value): self.state.crosshair_thickness = value
    def on_crosshair_rotation_changed(self, value): self.state.crosshair_rotation = value
    def on_crosshair_color_changed(self, color_hex): self.state.crosshair_color = color_hex
    def on_crosshair_style_changed(self, style): self.state.crosshair_line_style = style

    def on_reset_all_overlays(self):
        reply = QMessageBox.question(
            self, 'Confirm Reset',
            'Are you sure you want to reset the crosshair and remove all custom circles? This cannot be undone.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.state.crosshair_visible = True
            self.state.crosshair_offset_x = 0
            self.state.crosshair_offset_y = 0
            self.state.crosshair_thickness = 1
            self.state.crosshair_rotation = 0
            self.state.crosshair_color = "#39FF14"
            self.state.crosshair_line_style = "Solid"
            self.state.circles = [CircleState()]
            self.sync_ui_to_state()
            self.show_notification("All overlays reset to default.")

    def show_notification(self, message):
        self.notification.show_message(message)

    def sync_ui_to_state(self):
        self.settings_dialog.sync()
        self.apply_accessibility_settings()
        self.btn_night.setChecked(self.state.night_mode)
        from ui.styles import apply_application_theme
        apply_application_theme(self.state)
        
        self.btn_crosshair_vis.setChecked(self.state.crosshair_visible)
        self._update_visibility_button(self.btn_crosshair_vis, self.state.crosshair_visible)
        icon = get_visibility_icon(self.state.crosshair_visible, self.state.night_mode)
        self.tabs.setTabIcon(0, icon)
        self.slider_crosshair_offset_x.setValue(self.state.crosshair_offset_x)
        self.slider_crosshair_offset_y.setValue(self.state.crosshair_offset_y)
        self.slider_crosshair_thickness.setValue(self.state.crosshair_thickness)
        self.slider_crosshair_rotation.setValue(self.state.crosshair_rotation)
        self.palette_crosshair_color.set_color(self.state.crosshair_color)
        
        if self.state.crosshair_line_style == "Solid": self.btn_solid_crosshair.setChecked(True)
        elif self.state.crosshair_line_style == "Dashed": self.btn_dashed_crosshair.setChecked(True)
        else: self.btn_dotted_crosshair.setChecked(True)
        
        self.refresh_circle_tabs()
        if self.hud:
            self.hud.sync_ui_to_state()