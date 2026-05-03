from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel, QFrame, QButtonGroup
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt

def create_button(variant: str, text: str = None, icon_name: str = None, tooltip: str = None, checkable: bool = False, size: int = 32, auto_repeat: bool = False) -> QPushButton:
    """
    A factory function to create consistently styled QPushButtons.

    Args:
        variant (str): The style variant of the button. 
                       Supported: 'default', 'icon_round', 'icon_round_small', 'toggle_text', 'icon_flat'.
        text (str, optional): The text to display on the button.
        icon_name (str, optional): The name of the icon in 'assets/icons/'.
        tooltip (str, optional): The tooltip text.
        checkable (bool, optional): Whether the button is checkable.
        size (int, optional): The size for square buttons. Defaults to 32.
        auto_repeat (bool, optional): Whether the button continuously fires while held down.

    Returns:
        QPushButton: The configured button widget.
    """
    btn = QPushButton(text if text else "")
    if tooltip: btn.setToolTip(tooltip)
    if checkable: btn.setCheckable(True)
    if auto_repeat: btn.setAutoRepeat(True)

    if icon_name:
        btn.setIcon(QIcon(f'assets/icons/{icon_name}.svg'))

    if variant == 'icon_round':
        btn.setFixedSize(size, size)
        btn.setStyleSheet(f"border-radius: {size // 2}px;")
    elif variant == 'icon_round_small':
        small_size = 24
        icon_size = 12
        btn.setFixedSize(small_size, small_size)
        btn.setStyleSheet(f"border-radius: {small_size // 2}px; border: 0")
        if icon_name: btn.setIconSize(QSize(icon_size, icon_size))
    elif variant == 'icon_flat':
        btn.setStyleSheet("QPushButton { background: transparent; border: none; margin-bottom: 2px; margin-right: 0; } QPushButton:hover { background: rgba(255, 255, 255, 20); border-radius: 4px; }")
    
    return btn

def create_slider_row(slider, dec_icon, inc_icon, show_value=False, auto_toggle=None) -> QWidget:
    """Helper method to wrap a slider with decrement and increment buttons."""
    widget = QWidget()
    row = QHBoxLayout(widget)
    row.setContentsMargins(0, 0, 0, 0)
    
    if auto_toggle:
        row.addWidget(auto_toggle)
        
    btn_dec = create_button(variant='icon_round_small', icon_name=dec_icon, auto_repeat=True)
    btn_dec.clicked.connect(lambda checked, s=slider, st=-1: s.setValue(s.value() + st))
    row.addWidget(btn_dec)
    
    row.addWidget(slider)
    
    btn_inc = create_button(variant='icon_round_small', icon_name=inc_icon, auto_repeat=True)
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

def create_divider() -> QWidget:
    """Creates a visual horizontal separator line with padding."""
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(12, 6, 12, 6) # Left, Top, Right, Bottom padding
    line = QFrame()
    line.setObjectName("section_divider")
    line.setFixedHeight(1)
    layout.addWidget(line)
    return container

class LineStyleSelector(QWidget):
    """A horizontal button group component for selecting line styles."""
    def __init__(self, current_style, on_style_changed, parent=None):
        super().__init__(parent)
        self.on_style_changed = on_style_changed
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        self.btn_solid = create_button(variant='default', icon_name='solid', tooltip="Solid Line", checkable=True)
        self.btn_solid.clicked.connect(lambda: self.set_style("Solid"))
        self.btn_dashed = create_button(variant='default', icon_name='dashed', tooltip="Dashed Line", checkable=True)
        self.btn_dashed.clicked.connect(lambda: self.set_style("Dashed"))
        self.btn_dotted = create_button(variant='default', icon_name='dotted', tooltip="Dotted Line", checkable=True)
        self.btn_dotted.clicked.connect(lambda: self.set_style("Dotted"))
        
        self.button_group.addButton(self.btn_solid)
        self.button_group.addButton(self.btn_dashed)
        self.button_group.addButton(self.btn_dotted)
        
        layout.addWidget(self.btn_solid)
        layout.addWidget(self.btn_dashed)
        layout.addWidget(self.btn_dotted)
        layout.addStretch()
        
        self.set_style_ui(current_style)

    def set_style(self, style):
        self.on_style_changed(style)

    def set_style_ui(self, style):
        if style == "Solid": self.btn_solid.setChecked(True)
        elif style == "Dashed": self.btn_dashed.setChecked(True)
        else: self.btn_dotted.setChecked(True)