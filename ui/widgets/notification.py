from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from ui.styles import NOTIFICATION_LABEL

class NotificationWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(NOTIFICATION_LABEL)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(1000) # 1 second fade out
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        
        self.notification_timer = QTimer(self)
        self.notification_timer.setSingleShot(True)
        self.notification_timer.timeout.connect(self.fade_animation.start)

    def show_message(self, message: str):
        self.setText(message)
        self.opacity_effect.setOpacity(1.0) # Ensure it is fully visible
        self.fade_animation.stop() # Stop any currently running fade
        self.notification_timer.start(3000) # Wait 3 seconds before fading