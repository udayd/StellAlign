import cv2
from datetime import datetime
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLabel, QSplitter, QMessageBox
from PyQt6.QtCore import Qt, QRect, QUrl
from PyQt6.QtGui import QIcon, QImage, QPainter, QFont, QColor, QDesktopServices
from ui.video_widget import VideoWidget
from ui.control_panel import ControlPanel
from ui.hud import CameraHUD
from hardware.camera import CameraThread
from core.state import CollimationState
from core.workspace import WorkspaceManager
from ui.styles import LOADING_OVERLAY
from core.profiles import ProfileManager
from core.updater import UpdateChecker
from ui.widgets.components import create_button

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StellAlign")
        self.resize(1100, 850)
        self.setMinimumSize(1050, 800) # Ensure enough vertical space for the controls and notification

        # Initialize application state
        self.state = CollimationState()
        ProfileManager.load_global_settings(self.state)

        # Set up the main layout
        self.central_widget = QWidget()
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0) # Remove borders
        
        # Splitter to allow resizing the left panel
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # Initialize the HUD overlay first so the control panel can reference it
        self.camera_hud = CameraHUD(self.state)
        
        # Initialize the control panel
        self.control_panel = ControlPanel(self.state, hud=self.camera_hud)
        self.splitter.addWidget(self.control_panel)
        
        # Connect the screenshot button
        self.control_panel.workspace_widget.screenshot_requested.connect(self.take_screenshot)

        # Video & Overlays Container
        self.video_container = QWidget()
        video_layout = QGridLayout(self.video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_widget = VideoWidget()
        video_layout.addWidget(self.video_widget, 0, 0, 1, 1)
        video_layout.addWidget(self.camera_hud, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        self.loading_overlay = QLabel()
        self.loading_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_overlay.setStyleSheet(LOADING_OVERLAY)
        self.loading_overlay.hide()
        video_layout.addWidget(self.loading_overlay, 0, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.btn_fullscreen = create_button(variant='icon_round', icon_name='expand')
        self.btn_fullscreen.setStyleSheet("background: rgba(30, 30, 30, 150); border: none; border-radius: 16px; margin: 12px;")
        self.btn_fullscreen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        video_layout.addWidget(self.btn_fullscreen, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        self.splitter.addWidget(self.video_container)
        self.splitter.setStretchFactor(1, 1) # Force the video feed to take up the remaining space
        self.splitter.setCollapsible(0, False) # Prevent hiding the control panel entirely
        
        self.setCentralWidget(self.central_widget)

        # Initialize and start the camera thread
        self.camera_thread = CameraThread(self.state)
        # Connect the signal from the thread to the slot in the widget
        self.camera_thread.frame_received.connect(self.on_frame_received)
        self.camera_thread.connection_started.connect(self.show_loading)
        self.camera_thread.connection_failed.connect(self.show_connection_error)
        self.camera_thread.start()
        
        # Launch background update checker if enabled
        if self.state.auto_check_updates:
            self.update_checker = UpdateChecker(self.state.APP_VERSION)
            self.update_checker.update_available.connect(self.prompt_update)
            self.update_checker.start()

    def prompt_update(self, version, url):
        reply = QMessageBox.information(
            self, 
            "Update Available", 
            f"A new version of StellAlign ({version}) is available!\n\nWould you like to download it now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl(url))

    def on_frame_received(self, frame):
        if not self.loading_overlay.isHidden():
            self.hide_loading()
        self.video_widget.update_image(frame)

    def take_screenshot(self):
        frame = self.video_widget.get_current_frame()
        if frame is not None:
            # Convert BGR (OpenCV) to RGB (PyQt)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            
            # Create a true copy of the QImage to safely draw on it
            qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
            
            if self.state.watermark_screenshots:
                painter = QPainter(qt_image)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setOpacity(0.3)
                
                logo_size = 51
                logo = QIcon('assets/logos/logo.svg').pixmap(logo_size, logo_size)
                
                font = QFont("Roboto", 9, QFont.Weight.Bold)
                painter.setFont(font)
                painter.setPen(QColor("#FFFFFF"))
                
                text = "StellAlign"
                text_width = painter.fontMetrics().horizontalAdvance(text)
                text_height = painter.fontMetrics().height()
                
                margin = 20
                total_width = max(logo_size, text_width)
                
                start_x = w - total_width - margin
                start_y = h - logo_size - text_height - 5 - margin
                logo_x = start_x + (total_width - logo_size) // 2
                
                painter.drawPixmap(logo_x, start_y, logo)
                
                text_rect = QRect(start_x, start_y + logo_size + 5, total_width, text_height)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop, text)
                painter.end()
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            ext = self.state.screenshot_format
            filename = f"screenshot_{timestamp}{ext}"
            filepath = WorkspaceManager.get_screenshots_dir() / filename
            qt_image.save(str(filepath))
            self.control_panel.show_notification(f"Saved {filename}")

    def show_loading(self, message):
        content = f"<center><img src='assets/logos/logo.svg' width='128' height='128'><br><br>{message}</center>"
        self.loading_overlay.setText(content)
        self.loading_overlay.setStyleSheet(LOADING_OVERLAY)
        self.loading_overlay.show()
        
    def hide_loading(self):
        self.loading_overlay.hide()
        
    def show_connection_error(self):
        content = "<center><img src='assets/logos/logo.svg' width='128' height='128'><br><br>Failed to connect. Is the camera plugged in?</center>"
        self.loading_overlay.setText(content)
        self.loading_overlay.setStyleSheet(LOADING_OVERLAY.replace("rgba(0, 0, 0, 180)", "rgba(180, 0, 0, 180)"))
        self.loading_overlay.show()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.control_panel.show()
            self.btn_fullscreen.setIcon(QIcon('assets/icons/expand.svg'))
        else:
            self.showFullScreen()
            self.control_panel.hide()
            self.btn_fullscreen.setIcon(QIcon('assets/icons/compress.svg'))

    def closeEvent(self, event):
        # Safely shut down the camera when closing the app
        # If we don't do this, the camera hardware might stay locked
        ProfileManager.save_global_settings(self.state)
        self.camera_thread.stop()
        super().closeEvent(event)
