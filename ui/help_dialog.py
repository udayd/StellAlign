from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Collimation Cheatsheet")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        text = """
        <h3>Collimation Steps (Manual Mode)</h3>
        <ol>
            <li><b>Focuser Axis:</b> Create <i>Circle 1</i> and align it to the inner edge of your focuser drawtube. Click the <img src="assets/icons/crosshairs.svg" width="16" height="16" align="middle"> Anchor icon to set the True Center.</li>
            <br>
            <li><b>Secondary Placement:</b> Create <i>Circle 2</i>. Click the <img src="assets/icons/magnet.svg" width="16" height="16" align="middle"> Snap icon. Adjust your secondary mirror center-screw until the mirror fits perfectly inside the circle. <i>Tip: Turn on 'Mask Inside' to hide distracting reflections!</i></li>
            <br>
            <li><b>Secondary Tilt:</b> Create <i>Circle 3</i>. Click <img src="assets/icons/magnet.svg" width="16" height="16" align="middle"> Snap, and turn on the <img src="assets/icons/plus.svg" width="16" height="16" align="middle"> Center Mark. Size it to your primary mirror reflection. Adjust secondary tilt screws until the center mark sits perfectly inside the primary mirror's donut.</li>
            <br>
            <li><b>Primary Tilt:</b> Turn on the Main Crosshair. Adjust your primary mirror knobs at the back of the telescope until the reflection of the camera lens sits exactly centered on the crosshair.</li>
        </ol>
        """
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)