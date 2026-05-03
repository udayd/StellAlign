from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QCheckBox, QStackedWidget, QComboBox,
                             QDialog, QFormLayout, QButtonGroup)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from core.state import CollimationState

class CameraHUD(QWidget):
    def __init__(self, state: CollimationState, parent=None):
        super().__init__(parent)
        self.state = state
        
        self.setObjectName("hud_panel")
        self.setStyleSheet("QWidget#hud_panel { background-color: rgba(30, 30, 30, 220); border-radius: 8px; margin: 12px; }")
        scaled_width = int(344 * (self.state.ui_scale / 100.0))
        self.setFixedWidth(scaled_width)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(0)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.btn_tab_exp = QPushButton("Exposure")
        self.btn_tab_exp.setObjectName("hud_tab")
        self.btn_tab_exp.setCheckable(True)
        self.btn_tab_exp.setChecked(True)
        self.btn_tab_exp.clicked.connect(lambda: self.switch_tab(0))
        
        self.btn_tab_img = QPushButton("Image")
        self.btn_tab_img.setObjectName("hud_tab")
        self.btn_tab_img.setCheckable(True)
        self.btn_tab_img.clicked.connect(lambda: self.switch_tab(1))
        
        lbl_title = QLabel("Camera Controls")
        lbl_title.setStyleSheet("font-weight: bold; background: transparent;")
        
        self.btn_minimize = QPushButton()
        self.btn_minimize.setIcon(QIcon('assets/icons/chevron-down.svg'))
        self.btn_minimize.setFixedSize(24, 24)
        self.btn_minimize.setStyleSheet("background: transparent; border: none;")
        self.btn_minimize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_minimize.clicked.connect(self.toggle_minimize)
        
        header_layout.addWidget(self.btn_tab_exp)
        header_layout.addWidget(self.btn_tab_img)
        header_layout.addStretch()
        header_layout.addWidget(lbl_title)
        header_layout.addWidget(self.btn_minimize)
        main_layout.addLayout(header_layout)
        
        # Content
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        
        # Exposure Tab
        tab_exp = QWidget()
        tab_exp.setObjectName("tab_exp")
        tab_exp.setStyleSheet("QWidget#tab_exp { background-color: rgba(0, 0, 0, 120); border-radius: 6px; }")
        exp_layout = QFormLayout(tab_exp)
        exp_layout.setContentsMargins(12, 12, 12, 12) # Add padding so text doesn't touch the new black background
        
        self.slider_brightness = QSlider(Qt.Orientation.Horizontal); self.slider_brightness.setRange(0, 255); self.slider_brightness.setValue(self.state.brightness); self.slider_brightness.valueChanged.connect(self.on_brightness_changed)
        self.slider_contrast = QSlider(Qt.Orientation.Horizontal); self.slider_contrast.setRange(0, 255); self.slider_contrast.setValue(self.state.contrast); self.slider_contrast.valueChanged.connect(self.on_contrast_changed)
        self.slider_gamma = QSlider(Qt.Orientation.Horizontal); self.slider_gamma.setRange(10, 300); self.slider_gamma.setValue(self.state.gamma); self.slider_gamma.valueChanged.connect(self.on_gamma_changed)
        self.slider_exposure = QSlider(Qt.Orientation.Horizontal); self.slider_exposure.setRange(-15, 0); self.slider_exposure.setValue(self.state.exposure); self.slider_exposure.valueChanged.connect(self.on_exposure_changed)
        self.slider_gain = QSlider(Qt.Orientation.Horizontal); self.slider_gain.setRange(0, 255); self.slider_gain.setValue(self.state.gain); self.slider_gain.valueChanged.connect(self.on_gain_changed)
        self.slider_noise = QSlider(Qt.Orientation.Horizontal); self.slider_noise.setRange(1, 10); self.slider_noise.setValue(self.state.frame_averaging); self.slider_noise.valueChanged.connect(self.on_frame_averaging_changed)
        self.slider_focus = QSlider(Qt.Orientation.Horizontal); self.slider_focus.setRange(0, 255); self.slider_focus.setValue(self.state.focus); self.slider_focus.valueChanged.connect(self.on_focus_changed)
        
        self.btn_auto_focus = QPushButton("A")
        self.btn_auto_focus.setCheckable(True)
        self.btn_auto_focus.setChecked(self.state.auto_focus)
        self.btn_auto_focus.setFixedSize(24, 24)
        self.btn_auto_focus.setStyleSheet("QPushButton { border-radius: 12px; } QPushButton:checked { background-color: #2e7d32; font-weight: bold; color: white; border-radius: 12px; }")
        self.btn_auto_focus.toggled.connect(self.on_auto_focus_toggled)
        
        exp_layout.addRow("Brightness:", self._create_slider_row(self.slider_brightness, 'minus', 'plus', True))
        exp_layout.addRow("Contrast:", self._create_slider_row(self.slider_contrast, 'minus', 'plus', True))
        exp_layout.addRow("Gamma:", self._create_slider_row(self.slider_gamma, 'minus', 'plus', True))
        exp_layout.addRow("Exposure:", self._create_slider_row(self.slider_exposure, 'minus', 'plus', True))
        exp_layout.addRow("Gain:", self._create_slider_row(self.slider_gain, 'minus', 'plus', True))
        exp_layout.addRow("Focus:", self._create_slider_row(self.slider_focus, 'minus', 'plus', True, self.btn_auto_focus))
        exp_layout.addRow("Noise Red.:", self._create_slider_row(self.slider_noise, 'minus', 'plus', True))
        self.stack.addWidget(tab_exp)
        
        # Image Tab
        tab_img = QWidget()
        tab_img.setObjectName("tab_img")
        tab_img.setStyleSheet("QWidget#tab_img { background-color: rgba(0, 0, 0, 120); border-radius: 6px; }")
        img_layout = QFormLayout(tab_img)
        img_layout.setContentsMargins(12, 12, 12, 12) # Add padding so text doesn't touch the new black background
        
        self.chk_flip_h = QCheckBox("Flip Horizontal"); self.chk_flip_h.setChecked(self.state.flip_horizontal); self.chk_flip_h.toggled.connect(self.on_flip_h_toggled)
        self.chk_flip_v = QCheckBox("Flip Vertical"); self.chk_flip_v.setChecked(self.state.flip_vertical); self.chk_flip_v.toggled.connect(self.on_flip_v_toggled)
        self.chk_mono = QCheckBox("Monochrome"); self.chk_mono.setChecked(self.state.monochrome); self.chk_mono.toggled.connect(self.on_monochrome_toggled)
        self.chk_edge = QCheckBox("Edge Detect"); self.chk_edge.setChecked(self.state.edge_detection); self.chk_edge.toggled.connect(self.on_edge_toggled)
        
        grid = QHBoxLayout()
        col1 = QVBoxLayout(); col1.addWidget(self.chk_flip_h); col1.addWidget(self.chk_mono)
        col2 = QVBoxLayout(); col2.addWidget(self.chk_flip_v); col2.addWidget(self.chk_edge)
        grid.addLayout(col1); grid.addLayout(col2)
        
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal); self.slider_zoom.setRange(100, 500); self.slider_zoom.setValue(self.state.zoom); self.slider_zoom.valueChanged.connect(self.on_zoom_changed)
        self.slider_pan_x = QSlider(Qt.Orientation.Horizontal); self.slider_pan_x.setRange(-100, 100); self.slider_pan_x.setValue(self.state.pan_x); self.slider_pan_x.valueChanged.connect(self.on_pan_x_changed)
        self.slider_pan_y = QSlider(Qt.Orientation.Horizontal); self.slider_pan_y.setRange(-100, 100); self.slider_pan_y.setValue(self.state.pan_y); self.slider_pan_y.valueChanged.connect(self.on_pan_y_changed)
        
        img_layout.addRow(grid)
        img_layout.addRow("Zoom:", self._create_slider_row(self.slider_zoom, 'zoom-out', 'zoom-in', True))
        img_layout.addRow("Pan X:", self._create_slider_row(self.slider_pan_x, 'chevron-left', 'chevron-right', True))
        img_layout.addRow("Pan Y:", self._create_slider_row(self.slider_pan_y, 'chevron-up', 'chevron-down', True))
        
        btn_reset_view = QPushButton("Reset Zoom & Pan")
        btn_reset_view.clicked.connect(self.reset_zoom_pan)
        img_layout.addRow("", btn_reset_view)
        self.stack.addWidget(tab_img)
        
        content_layout.addWidget(self.stack)
        main_layout.addWidget(self.content_widget)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.btn_tab_exp.setChecked(index == 0)
        self.btn_tab_img.setChecked(index == 1)

    def toggle_minimize(self):
        is_visible = self.content_widget.isVisible()
        self.content_widget.setVisible(not is_visible)
        self.btn_tab_exp.setVisible(not is_visible)
        self.btn_tab_img.setVisible(not is_visible)
        icon_name = 'chevron-down.svg' if not is_visible else 'chevron-up.svg'
        self.btn_minimize.setIcon(QIcon(f'assets/icons/{icon_name}'))

    def reset_zoom_pan(self):
        self.slider_zoom.setValue(100)
        self.slider_pan_x.setValue(0)
        self.slider_pan_y.setValue(0)

    def _create_slider_row(self, slider, dec_icon, inc_icon, show_value=False, auto_toggle=None):
        widget = QWidget()
        row = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)
        
        if auto_toggle:
            row.addWidget(auto_toggle)
            
        btn_dec = QPushButton()
        btn_dec.setIcon(QIcon(f'assets/icons/{dec_icon}.svg'))
        btn_dec.setFixedSize(24, 24)
        btn_dec.clicked.connect(lambda checked, s=slider, st=-1: s.setValue(s.value() + st))
        row.addWidget(btn_dec)
        
        row.addWidget(slider)
        
        btn_inc = QPushButton()
        btn_inc.setIcon(QIcon(f'assets/icons/{inc_icon}.svg'))
        btn_inc.setFixedSize(24, 24)
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

    def sync_ui_to_state(self):
        self.slider_brightness.setValue(self.state.brightness)
        self.slider_contrast.setValue(self.state.contrast)
        self.slider_gamma.setValue(self.state.gamma)
        self.slider_exposure.setValue(self.state.exposure)
        self.slider_gain.setValue(self.state.gain)
        self.btn_auto_focus.setChecked(self.state.auto_focus)
        self.slider_focus.setValue(self.state.focus)
        self.slider_noise.setValue(self.state.frame_averaging)
        self.chk_flip_h.setChecked(self.state.flip_horizontal)
        self.chk_flip_v.setChecked(self.state.flip_vertical)
        self.chk_mono.setChecked(self.state.monochrome)
        self.chk_edge.setChecked(self.state.edge_detection)
        self.slider_zoom.setValue(self.state.zoom)
        self.slider_pan_x.setValue(self.state.pan_x)
        self.slider_pan_y.setValue(self.state.pan_y)

    def on_brightness_changed(self, v): self.state.brightness = v
    def on_contrast_changed(self, v): self.state.contrast = v
    def on_gamma_changed(self, v): self.state.gamma = v
    def on_exposure_changed(self, v): self.state.exposure = v
    def on_gain_changed(self, v): self.state.gain = v
    def on_auto_focus_toggled(self, c): self.state.auto_focus = c
    def on_focus_changed(self, v): self.state.focus = v
    def on_frame_averaging_changed(self, v): self.state.frame_averaging = v
    def on_flip_h_toggled(self, c): self.state.flip_horizontal = c
    def on_flip_v_toggled(self, c): self.state.flip_vertical = c
    def on_monochrome_toggled(self, c): self.state.monochrome = c
    def on_edge_toggled(self, c): self.state.edge_detection = c
    def on_zoom_changed(self, v): self.state.zoom = v
    def on_pan_x_changed(self, v): self.state.pan_x = v
    def on_pan_y_changed(self, v): self.state.pan_y = v