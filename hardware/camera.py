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
        self.cap = None
        self.zwo_cam = None
        self.using_zwo = False

    def _connect(self):
        # Close existing connections before attempting a new one
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
        if self.zwo_cam is not None:
            try:
                self.zwo_cam.stop_video_capture()
                self.zwo_cam.close()
            except:
                pass
            self.zwo_cam = None

        self.using_zwo = self.state.use_zwo_camera
        current_camera_index = self.state.camera_index

        if self.using_zwo:
            self.connection_started.emit("Initializing ZWO Camera...")
            try:
                import zwoasi as asi
                try:
                    asi.get_num_cameras()
                except Exception:
                    if self.state.zwo_sdk_path:
                        asi.init(self.state.zwo_sdk_path)
                    else:
                        raise ValueError("ZWO SDK Path is not set.")
                
                num_cameras = asi.get_num_cameras()
                if num_cameras == 0:
                    raise ValueError("No ZWO cameras found.")
                
                cam_idx = current_camera_index if current_camera_index < num_cameras else 0
                self.zwo_cam = asi.Camera(cam_idx)
                self.zwo_cam.set_image_type(asi.ASI_IMG_RGB24)
                self.zwo_cam.start_video_capture()
                self.connection_success.emit()
            except Exception as e:
                print(f"ZWO Connection Failed: {e}")
                self.connection_failed.emit()
                self.using_zwo = False
        else:
            self.connection_started.emit(f"Connecting to Camera {current_camera_index}...")
            self.cap = cv2.VideoCapture(current_camera_index)
            if self.cap.isOpened():
                self.connection_success.emit()
            else:
                self.connection_failed.emit()

    def run(self):
        self._connect()
        
        # Initialize tracking variables for camera properties
        last_res_w = self.state.resolution_width
        last_res_h = self.state.resolution_height
        last_brightness = self.state.brightness
        last_contrast = self.state.contrast
        last_exposure = self.state.exposure
        last_gain = self.state.gain
        last_auto_focus = self.state.auto_focus
        last_focus = self.state.focus
        last_use_zwo = self.state.use_zwo_camera
        last_cam_idx = self.state.camera_index
        
        # Set initial hardware values
        self._apply_hardware_settings(last_res_w, last_res_h, last_brightness, last_contrast, 
                                      last_exposure, last_gain, last_auto_focus, last_focus)
        
        while self._is_running:
            loop_start = time.time()
            needs_reconnect = False
            
            if self.state.use_zwo_camera != last_use_zwo:
                last_use_zwo = self.state.use_zwo_camera
                needs_reconnect = True

            if self.state.camera_index != last_cam_idx:
                last_cam_idx = self.state.camera_index
                needs_reconnect = True
                
            if self.state.resolution_width != last_res_w or self.state.resolution_height != last_res_h:
                last_res_w = self.state.resolution_width
                last_res_h = self.state.resolution_height
                needs_reconnect = True
                
            if needs_reconnect:
                self._connect()
                self._apply_hardware_settings(last_res_w, last_res_h, last_brightness, last_contrast, 
                                              last_exposure, last_gain, last_auto_focus, last_focus)

            # Update hardware if state has changed
            if self.state.brightness != last_brightness or \
               self.state.contrast != last_contrast or \
               self.state.exposure != last_exposure or \
               self.state.gain != last_gain or \
               self.state.auto_focus != last_auto_focus or \
               self.state.focus != last_focus:
               
                last_brightness = self.state.brightness
                last_contrast = self.state.contrast
                last_exposure = self.state.exposure
                last_gain = self.state.gain
                last_auto_focus = self.state.auto_focus
                last_focus = self.state.focus
                
                self._apply_hardware_settings(last_res_w, last_res_h, last_brightness, last_contrast, 
                                              last_exposure, last_gain, last_auto_focus, last_focus)

            ret, frame = False, None
            if self.using_zwo and self.zwo_cam:
                try:
                    raw_frame = self.zwo_cam.capture_video_frame(timeout=1000)
                    if raw_frame is not None:
                        roi = self.zwo_cam.get_roi_format()
                        w, h = roi[0], roi[1]
                        if not isinstance(raw_frame, np.ndarray):
                            raw_frame = np.frombuffer(raw_frame, dtype=np.uint8)
                        
                        expected_size = w * h * 3
                        if raw_frame.size == expected_size:
                            frame = raw_frame.reshape((h, w, 3))
                            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                            if w != last_res_w or h != last_res_h:
                                frame = cv2.resize(frame, (last_res_w, last_res_h))
                            ret = True
                except Exception:
                    ret = False
            elif not self.using_zwo and self.cap:
                ret, frame = self.cap.read()

            if ret and frame is not None:
                processed_frame = self.processor.process_frame(frame)
                self.frame_received.emit(processed_frame)
                
            if self.state.fps_limit > 0:
                elapsed = time.time() - loop_start
                target = 1.0 / self.state.fps_limit
                if elapsed < target:
                    time.sleep(target - elapsed)
                
        # Cleanup when the thread is stopped
        if self.cap:
            self.cap.release()
        if self.zwo_cam:
            self.zwo_cam.stop_video_capture()
            self.zwo_cam.close()

    def _apply_hardware_settings(self, res_w, res_h, brightness, contrast, exposure, gain, auto_focus, focus):
        if self.using_zwo and self.zwo_cam:
            try:
                import zwoasi as asi
                controls = self.zwo_cam.get_controls()
                
                if 'Exposure' in controls:
                    # Map UI exposure (-15 to 0) to ZWO microseconds (1ms to 1s)
                    exp_us = int(10 ** ((exposure + 15) / 15.0 * 3.0 + 3.0))
                    self.zwo_cam.set_control_value(asi.ASI_EXPOSURE, exp_us)
                    
                if 'Gain' in controls:
                    # Map UI gain to Max ZWO Gain limits automatically
                    zwo_max_gain = controls['Gain']['MaxValue']
                    zwo_gain = int((gain / 255.0) * zwo_max_gain)
                    self.zwo_cam.set_control_value(asi.ASI_GAIN, zwo_gain)
            except Exception as e:
                print(f"Error setting ZWO properties: {e}")
        elif not self.using_zwo and self.cap:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, res_w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res_h)
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
            self.cap.set(cv2.CAP_PROP_CONTRAST, contrast)
            self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
            self.cap.set(cv2.CAP_PROP_GAIN, 255 - gain)
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1 if auto_focus else 0)
            self.cap.set(cv2.CAP_PROP_FOCUS, focus)

    def stop(self):
        self._is_running = False
        self.wait()
