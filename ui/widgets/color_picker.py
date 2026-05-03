from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from ui.styles import color_picker_button

class InlineColorPicker(QWidget):
    """A modular horizontal palette of pre-defined colors."""
    COLORS = ["#39FF14", "#00E5FF", "#FF007F", "#FFFF00", "#FF3D00", "#FFFFFF"]
    
    def __init__(self, initial_color, on_color_changed, parent=None):
        super().__init__(parent)
        self.current_color = initial_color.upper()
        self.on_color_changed = on_color_changed
        self.buttons = {}
        
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(4)
        self.setLayout(self.h_layout)
        
        self.stretch_item = None
        self.build_palette()

    def build_palette(self):
        for btn in self.buttons.values():
            btn.setParent(None)
            btn.deleteLater()
        self.buttons.clear()
            
        if self.stretch_item:
            self.h_layout.removeItem(self.stretch_item)
            
        for color in self.COLORS:
            btn = QPushButton()
            btn.setFixedSize(20, 20)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, c=color: self.select_color(c))
            self.h_layout.addWidget(btn)
            self.buttons[color] = btn
            
        self.stretch_item = self.h_layout.addStretch()
        self.update_styles()

    def select_color(self, color):
        self.current_color = color
        self.update_styles()
        self.on_color_changed(color)

    def set_color(self, color_hex):
        self.current_color = color_hex.upper()
        self.update_styles()
        
    def update_styles(self):
        for color, btn in self.buttons.items():
            is_active = (color == self.current_color)
            btn.setStyleSheet(color_picker_button(color, is_active))