### 🔭 StellAlign - Project Knowledge Base

**Overview**
StellAlign is an open-source, Python-based desktop application for collimating reflector telescopes using a USB camera. It overlays customizable crosshairs and concentric circles on a live video feed to help users perfectly align their focuser, secondary, and primary mirrors.

**Tech Stack**
*   **Language:** Python
*   **Computer Vision:** OpenCV (`cv2`), NumPy
*   **GUI Framework:** PyQt6
*   **Theming & Icons:** `pyqtdarktheme` (Dark mode), Local SVG Icons (Twemoji)

**Core Architecture**
*   `main.py`: Application entry point. Initializes the workspace and applies the global dark theme.
*   `core/state.py`: Central `CollimationState` dataclass holding all variables, including a dynamic list of `CircleState` objects for infinite circles.
*   `core/workspace.py`: Manages the user's local directory (`Documents/StellAlign/`) for saving profiles and screenshots.
*   `core/profiles.py`: Handles saving, loading, and deleting the application state to/from `.json` files.
*   `hardware/camera.py`: A `QThread` worker capturing frames, managing hardware properties (exposure, gain, focus), and emitting connection state signals for UI loading overlays.
*   `vision/processor.py`: Image pipeline applying noise reduction, gamma, rotation, zoom/pan, masking, and finally drawing dashed/dotted crosshairs and circles.
*   `ui/main_window.py`: The primary GUI layout. Embeds the video feed and floats the HUD and Fullscreen buttons over the camera view.
*   `ui/video_widget.py`: Converts OpenCV BGR frames to PyQt `QImage` and handles aspect-ratio scaling.
*   `ui/control_panel.py`: The left sidebar housing Mode Selection, dynamic Circle Tabs, and the Workspace toolbar.
*   `ui/hud.py`: A floating, semi-transparent Camera Controls panel for live feed adjustments (Zoom, Pan, Gamma, Exposure).
*   `ui/settings_dialog.py`: Global Application Settings (Hardware selection, UI Scaling, Accessibility palettes).
*   `ui/wizard.py`: The Guided Assistant engine that programmatically steps through collimation instructions.
*   `ui/help_dialog.py`: A persistent HTML-based collimation cheatsheet.
*   `ui/styles.py`: Centralized sizing constants and dynamic stylesheet injection (Night Mode, Scaling, High Contrast).

**TODOs**
*   Fix the interactive cursor shapes (pointing-hand vs forbidden) not consistently applying to enabled/disabled PyQt widgets.

**Key Features**
1.  **The Anchor Workflow:** A "True Center" calibration system. Circles can "Set the Anchor" (moving the main crosshair) or "Snap to Anchor" to ensure perfect optical concentricity.
2.  **Dynamic Masking:** Inner and Outer masks with adjustable opacity to completely eliminate the "hall of mirrors" distraction in Newtonian reflectors.
3.  **Guided Assistant:** A telescope-specific wizard that automates the creation, masking, and positioning of circles step-by-step for beginners.
4.  **Advanced Camera Controls:** Real-time Frame Averaging (Noise reduction), Software Gamma, Digital Zoom/Pan, and Arbitrary Rotation.
5.  **Accessibility First:** Native support for UI scaling (up to 200%), Color-Blind safe palettes, high-contrast text overrides, dashed/dotted line styles, and a deep red Night Vision Mode to preserve dark adaptation.