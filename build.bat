@echo off
echo Building StellAlign Executable...
python -m PyInstaller --noconfirm --onedir --windowed --icon "assets/logos/logo.ico" --name "StellAlign" --add-data "assets/icons;assets/icons" --add-data "assets/logos;assets/logos" main.py
echo Build complete! You can find the executable in the dist/StellAlign folder.
pause