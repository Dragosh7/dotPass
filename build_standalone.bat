@echo off
echo [dotPass] Building standalone application...

REM === 1. Instalează dependențele ===
pip install pyinstaller pyarmor

REM === 2. Șterge builduri vechi ===
rmdir /s /q build
rmdir /s /q dist
del /q *.spec
rmdir /s /q protected
rmdir /s /q "..\dotPass - Password Manager"

REM === 3. Creează executabilul în folderul părinte ===
python -m PyInstaller --noconfirm --onefile --windowed ^
--distpath "..\dotPass - Password Manager" ^
--name dotPass ^
--add-data "core;core" ^
--add-data "ui;ui" ^
--add-data "ui/themes;ui/themes" ^
--add-data "ui/images;ui/images" ^
--add-data "ui/dialogs;ui/dialogs" ^
--add-data "utils;utils" ^
--add-data "utils/location;utils/location" ^
main.py

REM === 4. Gata ===
echo [dotPass] Build complete. The app can be found in this folder: ..\dotPass - Password Manager\
pause
