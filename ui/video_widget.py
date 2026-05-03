import cv2
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt
from ui.styles import VIDEO_WIDGET

class VideoWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setStyleSheet(VIDEO_WIDGET)
        self._current_frame = None
        
    def show_empty_state(self):
        size = 256
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setOpacity(0.1) # 10% opacity for a subtle watermark
        logo = QIcon("assets/logos/logo.svg").pixmap(size, size)
        painter.drawPixmap(0, 0, logo)
        painter.end()
        self.setPixmap(pixmap)

    def update_image(self, frame):
        # Store the original BGR frame for screenshots
        self._current_frame = frame
        
        # Convert BGR (OpenCV) to RGB (PyQt)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Get image dimensions
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        # Convert the numpy array into a QImage
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Scale the image to fit the label while keeping aspect ratio
        scaled_image = qt_image.scaled(self.width(), self.height(), 
                                       Qt.AspectRatioMode.KeepAspectRatio, 
                                       Qt.TransformationMode.SmoothTransformation)
        
        # Display it on the label
        self.setPixmap(QPixmap.fromImage(scaled_image))

    def get_current_frame(self):
        return self._current_frame
