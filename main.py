import sys
import os
import qdarktheme
from PyQt6.QtWidgets import QApplication, QPushButton, QCheckBox, QComboBox, QSlider, QTabBar
from PyQt6.QtCore import QObject, QEvent, Qt
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from core.workspace import WorkspaceManager
from ui.styles import apply_application_theme

class GlobalAppFilter(QObject):
    def __init__(self, state):
        super().__init__()
        self.state = state
        
    def eventFilter(self, obj, event):
        # Handle Global Tooltips
        if event.type() == QEvent.Type.ToolTip:
            if not self.state.show_tooltips:
                return True # Intercept and block the tooltip event
                
        # Handle Global Cursors for interactive elements
        elif event.type() in (QEvent.Type.Polish, QEvent.Type.Show, QEvent.Type.EnabledChange):
            if isinstance(obj, (QPushButton, QCheckBox, QComboBox, QSlider, QTabBar)):
                if obj.isEnabled():
                    obj.setCursor(Qt.CursorShape.PointingHandCursor)
                else:
                    obj.setCursor(Qt.CursorShape.ForbiddenCursor)
                    
        return super().eventFilter(obj, event)

def main():
    # Fix pathing for PyInstaller executable
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Initialize our document folders first thing
    WorkspaceManager.init_workspace()

    app = QApplication(sys.argv)
    
    # Set the global application icon (Taskbar / Dock)
    app.setWindowIcon(QIcon('assets/logos/logo.svg'))
    
    # Initialize and show the main window
    window = MainWindow()
    window.show()
    
    # Apply the theme (Dark or Night Vision)
    apply_application_theme(window.state)
    
    # Install global event filter to manage tooltips and cursors
    app.installEventFilter(GlobalAppFilter(window.state))
    
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
