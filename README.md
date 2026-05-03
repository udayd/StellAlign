# StellAlign

A precision collimation assistant for reflector telescopes using USB cameras. Open-source and designed for astrophotographers.

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