# StellAlign

A precision collimation assistant for reflector telescopes using USB or astronomy cameras. Open-source and designed for astrophotographers.

Currently, this is only available as a python script and a Windows executable. Other platforms are coming soon.

## Downloads

Check here for the latest builds: https://github.com/udayd/StellAlign/releases

## Features

**Key Features**
1.  **The Anchor Workflow:** A "True Center" calibration system. Circles can "Set the Anchor" (moving the main crosshair) or "Snap to Anchor" to ensure perfect optical concentricity.
2.  **Dynamic Masking:** Inner and Outer masks with adjustable opacity to completely eliminate the "hall of mirrors" distraction in Newtonian reflectors.
3.  **Guided Assistant:** A telescope-specific wizard that automates the creation, masking, and positioning of circles step-by-step for beginners.
4.  **Edge Detection:** Cleans up the hall of mirrors and displays high contrast edges, allowing you to easily see the edge of each plane.
5.  **Advanced Camera Controls:** Real-time Frame Averaging (Noise reduction), Software Gamma, Digital Zoom/Pan, and Arbitrary Rotation.
6.  **Accessibility First:** Native support for UI scaling (up to 200%), Color-Blind safe palettes, high-contrast text overrides, dashed/dotted line styles, and a deep red Night Vision Mode to preserve dark adaptation.

## Important Notes

*   When using an astronomy camera, it will need a lens in order to focus. You can use a relatively inexpensive one ($22 on 2025-05-03) like a [ZWO 150-degree Replacement Lens](https://optcorp.com/products/zwo-150-degree-replacement-lens) if it's threads fit your camera (or find one on Amazon). The advantage of this over a regular USB camera is that camera will fit your focuser properly, though you won't have the ability to autofocus.

##  TODOs
*   Fix the interactive cursor shapes (pointing-hand vs forbidden) not consistently applying to enabled/disabled PyQt widgets.
*   Create a build script or workflow for packaging the application on macOS (`.app` / `.dmg`).
*   Create a build script or workflow for packaging the application on Linux (AppImage or `.tar.gz`).
*   Implement a computer-vision powered Collimation Aid (Comet Tail, error HUD) to auto-detect reflections and guide real-time mechanical adjustments.
*   ASCOM integration for non-ZWO cameras
*   Create night mode icons
*   Reverse up / down icons so down is on the left side of the slider and up is on the right

## Installation

1. Clone this repository.
2. Install the requirements:
   `pip install -r requirements.txt`
3. Run the application:
   `python main.py`

## Packaging to an Executable (.exe)

To build a standalone Windows executable, ensure you have PyInstaller installed (`pip install pyinstaller`), then run the following command from the root directory:

```bash
py -m PyInstaller --noconfirm --onedir --windowed --icon "assets/logos/logo-256x256.ico" --name "StellAlign" --add-data "assets/icons;assets/icons" --add-data "assets/logos;assets/logos" main.py
```

Alternatively, Windows users can simply run the included `build.bat` script. The compiled application will be generated inside the `dist/StellAlign/` folder.
