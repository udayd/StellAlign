import cv2
import numpy as np
import time
from PyQt6.QtCore import QThread, pyqtSignal
from core.state import CollimationState
from vision.processor import FrameProcessor

class CameraThread(QThread):
    # This signal will broadcast the frame (as a numpy array) to the UI
    frame_received = pyqtSignal(np.ndarray)
    connection_started = pyqtSignal(str)
    connection_success = pyqtSignal()
    connection_failed = pyqtSignal()

    def __init__(self, state: CollimationState):
        super().__init__()
        self._is_running = True
        self.state = state
        self.processor = FrameProcessor(self.state)

    def run(self):
        # Open the connection to the USB Camera
        current_camera_index = self.state.camera_index
        self.connection_started.emit(f"Connecting to Camera {current_camera_index}...")
        cap = cv2.VideoCapture(current_camera_index)
        if cap.isOpened():
            self.connection_success.emit()
        else:
            self.connection_failed.emit()
        
        # Initialize tracking variables for camera properties
        last_res_w = self.state.resolution_width
        last_res_h = self.state.resolution_height
        last_brightness = self.state.brightness
        last_contrast = self.state.contrast
        last_exposure = self.state.exposure
        last_gain = self.state.gain
        last_auto_focus = self.state.auto_focus
        last_focus = self.state.focus
        
        # Set initial hardware values
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, last_res_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, last_res_h)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, last_brightness)
        cap.set(cv2.CAP_PROP_CONTRAST, last_contrast)
        cap.set(cv2.CAP_PROP_EXPOSURE, last_exposure)
        cap.set(cv2.CAP_PROP_GAIN, 255 - last_gain)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 1 if last_auto_focus else 0)
        cap.set(cv2.CAP_PROP_FOCUS, last_focus)
        
        while self._is_running:
            loop_start = time.time()
            needs_reconnect = False
            
            if self.state.camera_index != current_camera_index:
                current_camera_index = self.state.camera_index
                needs_reconnect = True
                
            if self.state.resolution_width != last_res_w or self.state.resolution_height != last_res_h:
                last_res_w = self.state.resolution_width
                last_res_h = self.state.resolution_height
                needs_reconnect = True
                
            if needs_reconnect:
                cap.release()
                self.connection_started.emit(f"Connecting to Camera {current_camera_index}...")
                cap = cv2.VideoCapture(current_camera_index)
                if cap.isOpened():
                    self.connection_success.emit()
                else:
                    self.connection_failed.emit()
                # Re-apply all hardware settings to the newly opened stream
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, last_res_w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, last_res_h)
                cap.set(cv2.CAP_PROP_BRIGHTNESS, last_brightness)
                cap.set(cv2.CAP_PROP_CONTRAST, last_contrast)
                cap.set(cv2.CAP_PROP_EXPOSURE, last_exposure)
                cap.set(cv2.CAP_PROP_GAIN, 255 - last_gain)
                cap.set(cv2.CAP_PROP_AUTOFOCUS, 1 if last_auto_focus else 0)
                cap.set(cv2.CAP_PROP_FOCUS, last_focus)

            # Update hardware if state has changed
            if self.state.brightness != last_brightness:
                last_brightness = self.state.brightness
                cap.set(cv2.CAP_PROP_BRIGHTNESS, last_brightness)
                
            if self.state.contrast != last_contrast:
                last_contrast = self.state.contrast
                cap.set(cv2.CAP_PROP_CONTRAST, last_contrast)
                
            if self.state.exposure != last_exposure:
                last_exposure = self.state.exposure
                cap.set(cv2.CAP_PROP_EXPOSURE, last_exposure)
                
            if self.state.gain != last_gain:
                last_gain = self.state.gain
                cap.set(cv2.CAP_PROP_GAIN, 255 - last_gain)
                
            if self.state.auto_focus != last_auto_focus:
                last_auto_focus = self.state.auto_focus
                cap.set(cv2.CAP_PROP_AUTOFOCUS, 1 if last_auto_focus else 0)
                
            if self.state.focus != last_focus:
                last_focus = self.state.focus
                cap.set(cv2.CAP_PROP_FOCUS, last_focus)

            ret, frame = cap.read()
            if ret:
                # Process the frame to add overlays based on state
                processed_frame = self.processor.process_frame(frame)
                # Emit the raw frame to anyone listening (our UI)
                self.frame_received.emit(processed_frame)
                
            if self.state.fps_limit > 0:
                elapsed = time.time() - loop_start
                target = 1.0 / self.state.fps_limit
                if elapsed < target:
                    time.sleep(target - elapsed)
                
        # Cleanup when the thread is stopped
        cap.release()

    def stop(self):
        self._is_running = False
        self.wait()
