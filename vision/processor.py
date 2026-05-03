import cv2
import numpy as np
from core.state import CollimationState

class FrameProcessor:
    def __init__(self, state: CollimationState):
        self.state = state
        self.frame_buffer = []
        self._last_gamma = -1
        self._gamma_table = None
        self._solid_buffer = None
        self._mask_buffer = None

    def _draw_styled_line(self, img, pt1, pt2, color, thickness, style):
        if style == "Solid":
            cv2.line(img, pt1, pt2, color, thickness)
            return
            
        dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
        if dist == 0: return
        
        dash_length = 15 if style == "Dashed" else 3
        gap_length = 15 if style == "Dashed" else 10
        dashes = int(dist / (dash_length + gap_length))
        
        if dashes == 0:
            cv2.line(img, pt1, pt2, color, thickness)
            return
            
        dx, dy = (pt2[0] - pt1[0]) / dist, (pt2[1] - pt1[1]) / dist
        for i in range(dashes + 1):
            start_x = int(pt1[0] + (i * (dash_length + gap_length)) * dx)
            start_y = int(pt1[1] + (i * (dash_length + gap_length)) * dy)
            if np.linalg.norm(np.array([start_x, start_y]) - np.array(pt1)) > dist: break
            end_x, end_y = int(start_x + dash_length * dx), int(start_y + dash_length * dy)
            if np.linalg.norm(np.array([end_x, end_y]) - np.array(pt1)) > dist: end_x, end_y = pt2
            cv2.line(img, (start_x, start_y), (end_x, end_y), color, thickness)

    def _draw_styled_circle(self, img, center, radius, color, thickness, style):
        if style == "Solid":
            cv2.circle(img, center, radius, color, thickness)
            return
            
        dash_length = 15 if style == "Dashed" else 3
        gap_length = 15 if style == "Dashed" else 10
        circumference = 2 * np.pi * radius
        if circumference == 0: return
        
        dashes = int(circumference / (dash_length + gap_length))
        if dashes == 0:
            cv2.circle(img, center, radius, color, thickness)
            return
            
        angle_step = 360 / dashes
        dash_angle = (dash_length / (dash_length + gap_length)) * angle_step
        for i in range(dashes):
            start_angle = i * angle_step
            cv2.ellipse(img, center, (radius, radius), 0, start_angle, start_angle + dash_angle, color, thickness)

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        # Make a copy so we don't modify the original raw frame
        processed_frame = frame.copy()
        
        # Pre-allocate or resize buffers for masking
        if self._solid_buffer is None or self._solid_buffer.shape != processed_frame.shape:
            self._solid_buffer = np.zeros_like(processed_frame)
            self._mask_buffer = np.zeros_like(processed_frame)
        
        # 0. Frame Averaging (Noise Reduction)
        if self.state.frame_averaging > 1:
            # Clear buffer if resolution changed to avoid shape mismatch errors
            if self.frame_buffer and self.frame_buffer[0].shape != processed_frame.shape:
                self.frame_buffer.clear()
            self.frame_buffer.append(processed_frame)
            if len(self.frame_buffer) > self.state.frame_averaging:
                self.frame_buffer.pop(0)
            processed_frame = np.mean(self.frame_buffer, axis=0).astype(np.uint8)
        else:
            self.frame_buffer.clear()
            
        # 0.5. Software Gamma
        if self.state.gamma != 100:
            if self.state.gamma != self._last_gamma:
                gamma_val = self.state.gamma / 100.0
                inv_gamma = 1.0 / gamma_val
                self._gamma_table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
                self._last_gamma = self.state.gamma
            processed_frame = cv2.LUT(processed_frame, self._gamma_table)
            
        # 0.7. Monochrome
        if self.state.monochrome:
            gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
            processed_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # 1. Apply Image Flipping
        if self.state.flip_horizontal and self.state.flip_vertical:
            processed_frame = cv2.flip(processed_frame, -1)
        elif self.state.flip_horizontal:
            processed_frame = cv2.flip(processed_frame, 1)
        elif self.state.flip_vertical:
            processed_frame = cv2.flip(processed_frame, 0)
            
        # 1.5. Apply Rotation
        if self.state.rotation_angle != 0:
            h, w = processed_frame.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, self.state.rotation_angle, 1.0)
            processed_frame = cv2.warpAffine(processed_frame, M, (w, h))
            
        # 1.8. Digital Zoom & Pan
        if self.state.zoom > 100:
            h, w = processed_frame.shape[:2]
            scale = self.state.zoom / 100.0
            half_w = int(w / (2 * scale))
            half_h = int(h / (2 * scale))
            
            # Pan percentages (-100 to 100) mapped to available offset pixels
            pan_x_offset = int((self.state.pan_x / 100.0) * (w / 2 - half_w))
            pan_y_offset = int((self.state.pan_y / 100.0) * (h / 2 - half_h))
            
            cx = max(half_w, min(w - half_w, (w // 2) + pan_x_offset))
            cy = max(half_h, min(h - half_h, (h // 2) + pan_y_offset))
            
            cropped = processed_frame[cy - half_h : cy + half_h, cx - half_w : cx + half_w]
            processed_frame = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
            
        # 2. Apply Edge Detection
        if self.state.edge_detection:
            gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
            # Detect edges using Canny
            edges = cv2.Canny(gray, 50, 150)
            # Convert back to BGR to allow colored overlays
            processed_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        h, w = processed_frame.shape[:2]
        center_x, center_y = w // 2, h // 2

        if self.state.crosshair_visible:
            # Parse the hex color into a BGR tuple for OpenCV
            h_cross = self.state.crosshair_color.lstrip('#')
            bgr_cross_color = tuple(int(h_cross[i:i+2], 16) for i in (4, 2, 0))
            
            cross_x = center_x + self.state.crosshair_offset_x
            cross_y = center_y + self.state.crosshair_offset_y
            self._draw_styled_line(processed_frame, (cross_x, 0), (cross_x, h), bgr_cross_color, self.state.crosshair_thickness, self.state.crosshair_line_style)
            self._draw_styled_line(processed_frame, (0, cross_y), (w, cross_y), bgr_cross_color, self.state.crosshair_thickness, self.state.crosshair_line_style)

        for circle in self.state.circles:
            if not circle.visible:
                continue
                
            # Parse the hex color
            h_color = circle.color.lstrip('#')
            bgr_color = tuple(int(h_color[i:i+2], 16) for i in (4, 2, 0))
            
            circle_x = center_x + circle.offset_x
            circle_y = center_y + circle.offset_y
            
            # Apply Masking
            if circle.mask_mode != 'none':
                opacity = circle.mask_opacity / 100.0
                
                # Reuse pre-allocated buffers
                self._solid_buffer[:] = bgr_color
                self._mask_buffer.fill(0)
                
                darkened_frame = cv2.addWeighted(processed_frame, 1.0 - opacity, self._solid_buffer, opacity * 0.3, 0)
                cv2.circle(self._mask_buffer, (circle_x, circle_y), circle.radius, (255, 255, 255), -1)
                
                if circle.mask_mode == 'inside':
                    processed_frame = np.where(self._mask_buffer == 255, darkened_frame, processed_frame)
                elif circle.mask_mode == 'outside':
                    processed_frame = np.where(self._mask_buffer == 0, darkened_frame, processed_frame)
                    
            self._draw_styled_circle(processed_frame, (circle_x, circle_y), circle.radius, bgr_color, circle.thickness, circle.line_style)
            
            if circle.center_mark_visible:
                mark_size = 10
                thickness = max(1, circle.thickness - 1)
                cv2.line(processed_frame, (circle_x - mark_size, circle_y), (circle_x + mark_size, circle_y), bgr_color, thickness)
                cv2.line(processed_frame, (circle_x, circle_y - mark_size), (circle_x, circle_y + mark_size), bgr_color, thickness)

        return processed_frame
