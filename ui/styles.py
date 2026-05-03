"""Centralized stylesheets for the StellAlign application."""
import qdarktheme
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

# Static Styles
VIDEO_WIDGET = "background-color: black !important;"
NOTIFICATION_LABEL = "color: #4CAF50; font-weight: bold;" # Green success text
LOADING_OVERLAY = "background-color: rgba(0, 0, 0, 180); color: white; font-size: 20px; font-weight: bold; border-radius: 12px; padding: 30px;"

# Structural Styles (Sizing, Padding, and Spacing)
PANEL_WIDTH = 320 # Minimum width of the entire left column
MAX_PANEL_WIDTH = 600 # Maximum width of the left column when dragged
GROUP_SPACING = 15 # Margins between the major sections (Camera, Image, Workspace)
ROW_SPACING = 12 # Margins between individual rows (e.g., Device and Resolution)
SECTION_MARGINS = (12, 16, 12, 12) # Padding inside the sections (Left, Top, Right, Bottom)

# Dynamic Styles
def color_picker_button(color_hex: str, is_active: bool) -> str:
    border = "2px solid #FFFFFF" if is_active else "1px solid #555555"
    return f"background-color: {color_hex}; border: {border}; border-radius: 10px;"

_icon_cache = {}

def get_visibility_icon(is_visible: bool, is_night_mode: bool) -> QIcon:
    cache_key = (is_visible, is_night_mode)
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
        
    size = 24
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    if not is_visible:
        color = QColor("#c62828") # Red
    else:
        color = QColor("#FFFFFF") if is_night_mode else QColor("#2e7d32") # White or Green
        
    painter.setBrush(color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 16, 16) # Perfectly center a 16x16 circle in the 24x24 box
    painter.end()
    
    icon = QIcon(pixmap)
    _icon_cache[cache_key] = icon
    return icon

GLOBAL_STYLESHEET = """
* {
    font-family: "Roboto", "Segoe UI", sans-serif;
}
QCheckBox::indicator:checked, QGroupBox::title { color: #00E5FF; }
QSlider::handle:horizontal { background: #00E5FF; }
QSlider::handle:horizontal:disabled { background: #555555; }
QSlider::sub-page:horizontal { background: #008899; }
QSlider::sub-page:horizontal:disabled { background: #333333; }

QPushButton {
    border-radius: 12px;
}
QPushButton#hud_tab {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0px;
    padding: 4px 12px;
    color: #aaaaaa;
}
QPushButton#hud_tab:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 10);
}
QPushButton#hud_tab:checked {
    color: #ffffff;
    border-bottom: 2px solid #00E5FF;
    font-weight: bold;
    background-color: rgba(0, 0, 0, 120);
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QCheckBox, QCheckBox:hover, QCheckBox::indicator:hover {
    border: 0;
}
"""

NIGHT_MODE_STYLESHEET = """
QWidget { background-color: #120000; color: #ff5555; }
QLabel, QCheckBox { background-color: transparent; }
QPushButton, QComboBox, QSpinBox, QLineEdit { background-color: #2a0000; border: 1px solid #550000; color: #ff5555; }
QPushButton { border-radius: 12px; }
QPushButton:hover, QComboBox:hover { background-color: #3d0000; border: 1px solid #ff0000; }
QPushButton:checked { background-color: #550000; border: 1px solid #ff3333; }
QPushButton:disabled, QComboBox:disabled { background-color: #0f0000; border: 1px solid #1a0000; color: #551111; }
QGroupBox { border: 1px solid #550000; }
QSlider::groove:horizontal { background: #2a0000; }
QSlider::sub-page:horizontal { background: #aa0000; }
QSlider::add-page:horizontal { background: #1a0000; }
QSlider::handle:horizontal { background: #ff0000; }
QSlider::handle:horizontal:disabled { background: #551111; }
QSlider::sub-page:horizontal:disabled { background: #330000; }
QTabWidget::pane { border: 1px solid #550000; background: transparent; }
QTabBar::tab { background-color: #1a0000; border: 1px solid #550000; color: #ff5555; }
QTabBar::tab:selected { background-color: #2a0000; color: #ffaaaa; }
QWidget#hud_panel { background-color: rgba(50, 0, 0, 220) !important; }
QWidget#tab_exp, QWidget#tab_img { background-color: rgba(60, 0, 0, 150) !important; }
QPushButton#hud_tab { color: #cc5555; }
QPushButton#hud_tab:hover { color: #ffaaaa; background: rgba(255, 0, 0, 10); }
QPushButton#hud_tab:checked { color: #ffffff; border-bottom: 2px solid #ff3333; background-color: rgba(60, 0, 0, 150) !important; }
"""

def apply_application_theme(state):
    app = QApplication.instance()
    if not app:
        return
    base_css = qdarktheme.load_stylesheet("dark") + "\n" + GLOBAL_STYLESHEET
    
    font_size = int(10 * (state.ui_scale / 100.0))
    scale_css = f"QWidget {{ font-size: {font_size}pt; }}\n"
    
    contrast_css = ""
    if state.high_contrast_text:
        contrast_css = "QLabel, QCheckBox, QPushButton, QComboBox, QGroupBox { color: #FFFFFF !important; font-weight: bold; }\n"
        
    final_css = base_css + "\n" + scale_css + contrast_css
    
    if state.night_mode:
        final_css += "\n" + NIGHT_MODE_STYLESHEET
        
    app.setStyleSheet(final_css)