from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon

def create_button(variant: str, text: str = None, icon_name: str = None, tooltip: str = None, checkable: bool = False, size: int = 32, auto_repeat: bool = False) -> QPushButton:
    """
    A factory function to create consistently styled QPushButtons.

    Args:
        variant (str): The style variant of the button. 
                       Supported: 'default', 'icon_round', 'toggle_text', 'icon_flat'.
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
    elif variant == 'icon_flat':
        btn.setStyleSheet("QPushButton { background: transparent; border: none; margin-bottom: 2px; margin-right: 0; } QPushButton:hover { background: rgba(255, 255, 255, 20); border-radius: 4px; }")
    
    return btn