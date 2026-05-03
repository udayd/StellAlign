from dataclasses import dataclass, field

@dataclass
class CircleState:
    name: str = "Circle 1"
    visible: bool = True
    radius: int = 150
    offset_x: int = 0
    offset_y: int = 0
    thickness: int = 2
    color: str = "#00E5FF" # Electric Cyan default
    line_style: str = "Solid" # "Solid", "Dashed", or "Dotted"
    center_mark_visible: bool = False
    mask_mode: str = "none" # "none", "inside", or "outside"
    mask_opacity: int = 85

@dataclass
class CollimationState:
    """Holds the current state of the application's overlays and settings."""
    APP_VERSION: str = "v0.1.0"
    crosshair_visible: bool = True
    crosshair_offset_x: int = 0
    crosshair_offset_y: int = 0
    crosshair_thickness: int = 1
    crosshair_color: str = "#39FF14" # Neon Green default
    crosshair_line_style: str = "Solid"
    circles: list[CircleState] = field(default_factory=lambda: [CircleState()])
    camera_index: int = 0
    resolution_width: int = 640
    resolution_height: int = 480
    flip_horizontal: bool = False
    flip_vertical: bool = False
    monochrome: bool = False
    edge_detection: bool = False
    rotation_angle: int = 0
    zoom: int = 100
    pan_x: int = 0
    pan_y: int = 0
    gamma: int = 100
    frame_averaging: int = 1
    brightness: int = 128
    contrast: int = 128
    exposure: int = -5
    gain: int = 128
    auto_focus: bool = True
    focus: int = 0
    night_mode: bool = False
    ui_scale: int = 100
    high_contrast_text: bool = False
    color_blind_palette: bool = False
    show_tooltips: bool = True
    remember_hardware: bool = True
    fps_limit: int = 30
    screenshot_format: str = ".png"
    watermark_screenshots: bool = True
    auto_check_updates: bool = True
