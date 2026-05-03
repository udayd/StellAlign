from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QTabWidget, QWidget, QFormLayout, QCheckBox, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from core.state import CollimationState

class GlobalSettingsDialog(QDialog):
    def __init__(self, state: CollimationState, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Settings")
        self.state = state
        scaled_min_width = int(380 * (self.state.ui_scale / 100.0))
        self.setMinimumWidth(scaled_min_width)
        
        main_layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        # --- Hardware Tab ---
        tab_hw = QWidget()
        hw_layout = QFormLayout(tab_hw)
        
        self.combo_camera = QComboBox()
        self._populate_cameras()
        if self.state.camera_index < self.combo_camera.count():
            self.combo_camera.setCurrentIndex(self.state.camera_index)
        self.combo_camera.currentIndexChanged.connect(self.on_camera_changed)
        
        self.combo_resolution = QComboBox()
        self.combo_resolution.addItems(["640x480", "800x600", "1280x720", "1920x1080"])
        self.combo_resolution.setCurrentText(f"{self.state.resolution_width}x{self.state.resolution_height}")
        self.combo_resolution.currentTextChanged.connect(self.on_resolution_changed)
        
        self.chk_use_zwo = QCheckBox("Enable Native ZWO Camera Support")
        self.chk_use_zwo.setChecked(self.state.use_zwo_camera)
        self.chk_use_zwo.toggled.connect(self.on_use_zwo_toggled)

        self.input_zwo_path = QLineEdit()
        self.input_zwo_path.setText(self.state.zwo_sdk_path)
        self.input_zwo_path.setPlaceholderText("Path to ASICamera2.dll or libASICamera2.so")
        self.input_zwo_path.textChanged.connect(self.on_zwo_path_changed)
        
        self.btn_browse_zwo = QPushButton("Browse...")
        self.btn_browse_zwo.clicked.connect(self.browse_zwo_sdk)
        
        self.zwo_path_layout = QHBoxLayout()
        self.zwo_path_layout.addWidget(self.input_zwo_path)
        self.zwo_path_layout.addWidget(self.btn_browse_zwo)
        
        hw_layout.addRow("Device:", self.combo_camera)
        hw_layout.addRow("Resolution:", self.combo_resolution)
        hw_layout.addRow("", self.chk_use_zwo)
        hw_layout.addRow("ZWO SDK Path:", self.zwo_path_layout)
        self.tabs.addTab(tab_hw, "Hardware")
        
        self._update_zwo_visibility(self.state.use_zwo_camera)
        
        # --- Accessibility Tab ---
        tab_acc = QWidget()
        acc_layout = QFormLayout(tab_acc)
        
        self.combo_scale = QComboBox()
        self.combo_scale.addItems(["100%", "125%", "150%", "175%", "200%"])
        self.combo_scale.setCurrentText(f"{self.state.ui_scale}%")
        self.combo_scale.currentTextChanged.connect(self.on_scale_changed)
        
        self.chk_color_blind = QCheckBox("Color-Blind Safe Palette")
        self.chk_color_blind.setChecked(self.state.color_blind_palette)
        self.chk_color_blind.toggled.connect(self.on_color_blind_toggled)
        
        self.chk_high_contrast = QCheckBox("High Contrast Text")
        self.chk_high_contrast.setChecked(self.state.high_contrast_text)
        self.chk_high_contrast.toggled.connect(self.on_high_contrast_toggled)
        
        acc_layout.addRow("UI Scale:", self.combo_scale)
        acc_layout.addRow("", self.chk_color_blind)
        acc_layout.addRow("", self.chk_high_contrast)
        self.tabs.addTab(tab_acc, "Accessibility")
        
        # --- Behaviors Tab ---
        tab_beh = QWidget()
        beh_layout = QFormLayout(tab_beh)
        
        self.chk_tooltips = QCheckBox("Show Interface Tooltips")
        self.chk_tooltips.setChecked(self.state.show_tooltips)
        self.chk_tooltips.toggled.connect(self.on_tooltips_toggled)
        
        self.chk_remember_hw = QCheckBox("Remember Camera & Resolution on Startup")
        self.chk_remember_hw.setChecked(self.state.remember_hardware)
        self.chk_remember_hw.toggled.connect(self.on_remember_hw_toggled)
        
        self.combo_fps = QComboBox()
        self.combo_fps.addItems(["15 FPS", "30 FPS", "60 FPS", "Uncapped"])
        fps_map = {15: "15 FPS", 30: "30 FPS", 60: "60 FPS", 0: "Uncapped"}
        self.combo_fps.setCurrentText(fps_map.get(self.state.fps_limit, "Uncapped"))
        self.combo_fps.currentTextChanged.connect(self.on_fps_changed)
        
        self.combo_screenshot = QComboBox()
        self.combo_screenshot.addItems([".png", ".jpg", ".tiff"])
        self.combo_screenshot.setCurrentText(self.state.screenshot_format)
        self.combo_screenshot.currentTextChanged.connect(self.on_screenshot_changed)
        
        self.chk_watermark = QCheckBox("Add Watermark to Screenshots")
        self.chk_watermark.setChecked(self.state.watermark_screenshots)
        self.chk_watermark.toggled.connect(self.on_watermark_toggled)
        
        self.chk_updates = QCheckBox("Automatically check for updates on startup")
        self.chk_updates.setChecked(self.state.auto_check_updates)
        self.chk_updates.toggled.connect(self.on_updates_toggled)
        
        beh_layout.addRow("", self.chk_tooltips)
        beh_layout.addRow("", self.chk_remember_hw)
        beh_layout.addRow("", self.chk_watermark)
        beh_layout.addRow("", self.chk_updates)
        beh_layout.addRow("Max Framerate:", self.combo_fps)
        beh_layout.addRow("Screenshot Format:", self.combo_screenshot)
        self.tabs.addTab(tab_beh, "Behaviors")
        
        # --- About Tab ---
        tab_about = QWidget()
        about_layout = QVBoxLayout(tab_about)
        about_content = QLabel(
            "<center>"
            "<img src='assets/logos/logo.svg' width='80' height='80'><br><br>"
            "<h2 style='color: #00E5FF; margin: 0;'>StellAlign</h2>"
            f"<p style='color: #aaaaaa; margin: 0;'>{self.state.APP_VERSION}</p><br>"
            "<p>Precision collimation tools for reflector telescopes.</p>"
            "<p>Open-source and designed for astrophotographers.</p>"
            "</center>"
        )
        about_content.setTextFormat(Qt.TextFormat.RichText)
        about_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(about_content)
        
        self.btn_check_updates = QPushButton("Check for Updates")
        self.btn_check_updates.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_updates.clicked.connect(self.check_for_updates)
        about_layout.addWidget(self.btn_check_updates, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.tabs.addTab(tab_about, "About")
        
        main_layout.addWidget(self.tabs)
        
        btn_close = QPushButton("Done")
        btn_close.clicked.connect(self.accept)
        main_layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    def on_camera_changed(self, idx): self.state.camera_index = idx
    def on_resolution_changed(self, text):
        w, h = map(int, text.split('x'))
        self.state.resolution_width = w
        self.state.resolution_height = h
    def on_use_zwo_toggled(self, checked):
        self.state.use_zwo_camera = checked
        self._update_zwo_visibility(checked)

    def _update_zwo_visibility(self, visible):
        self.input_zwo_path.setVisible(visible)
        self.btn_browse_zwo.setVisible(visible)
        self.tabs.widget(0).layout().labelForField(self.zwo_path_layout).setVisible(visible)

    def on_zwo_path_changed(self, text): self.state.zwo_sdk_path = text
    def browse_zwo_sdk(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select ZWO SDK Library", "", "Shared Libraries (*.dll *.so);;All Files (*)")
        if path:
            self.input_zwo_path.setText(path)
    def on_scale_changed(self, text): 
        self.state.ui_scale = int(text.replace("%", ""))
        scaled_min_width = int(380 * (self.state.ui_scale / 100.0))
        self.setMinimumWidth(scaled_min_width)
        self._apply_live_settings()
    def on_color_blind_toggled(self, checked): 
        self.state.color_blind_palette = checked
        self._apply_live_settings()
    def on_high_contrast_toggled(self, checked): 
        self.state.high_contrast_text = checked
        self._apply_live_settings()
    def on_tooltips_toggled(self, checked): self.state.show_tooltips = checked
    def on_remember_hw_toggled(self, checked): self.state.remember_hardware = checked
    def on_fps_changed(self, text):
        if text == "Uncapped": self.state.fps_limit = 0
        else: self.state.fps_limit = int(text.split(" ")[0])
    def on_screenshot_changed(self, text): self.state.screenshot_format = text
    def on_watermark_toggled(self, checked): self.state.watermark_screenshots = checked
    def on_updates_toggled(self, checked): self.state.auto_check_updates = checked

    def check_for_updates(self):
        QDesktopServices.openUrl(QUrl("https://github.com/udayd/StellAlign/releases"))

    def _populate_cameras(self):
        self.combo_camera.clear()
        try:
            # Requires: pip install pygrabber
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            devices = graph.get_input_devices()
            if devices:
                self.combo_camera.addItems([f"{i}: {name}" for i, name in enumerate(devices)])
                return
        except ImportError:
            pass
            
        # Fallback if pygrabber isn't installed or fails
        self.combo_camera.addItems([f"Camera {i}" for i in range(5)])

    def _apply_live_settings(self):
        parent = self.parent()
        if parent and hasattr(parent, 'apply_accessibility_settings'):
            parent.apply_accessibility_settings()
        from ui.styles import apply_application_theme
        apply_application_theme(self.state)

    def sync(self):
        self.combo_camera.blockSignals(True)
        self._populate_cameras()
        if self.state.camera_index < self.combo_camera.count():
            self.combo_camera.setCurrentIndex(self.state.camera_index)
        else:
            self.combo_camera.setCurrentIndex(0)
        self.combo_camera.blockSignals(False)
        
        self.combo_resolution.setCurrentText(f"{self.state.resolution_width}x{self.state.resolution_height}")
        self.combo_scale.setCurrentText(f"{self.state.ui_scale}%")
        self.chk_color_blind.setChecked(self.state.color_blind_palette)
        self.chk_high_contrast.setChecked(self.state.high_contrast_text)
        self.chk_tooltips.setChecked(self.state.show_tooltips)
        self.chk_remember_hw.setChecked(self.state.remember_hardware)
        self.chk_use_zwo.setChecked(self.state.use_zwo_camera)
        self.input_zwo_path.setText(self.state.zwo_sdk_path)
        self._update_zwo_visibility(self.state.use_zwo_camera)
        fps_map = {15: "15 FPS", 30: "30 FPS", 60: "60 FPS", 0: "Uncapped"}
        self.combo_fps.setCurrentText(fps_map.get(self.state.fps_limit, "Uncapped"))
        self.combo_screenshot.setCurrentText(self.state.screenshot_format)
        self.chk_watermark.setChecked(self.state.watermark_screenshots)
        self.chk_updates.setChecked(self.state.auto_check_updates)