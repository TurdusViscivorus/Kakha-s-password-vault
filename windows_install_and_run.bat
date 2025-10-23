@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
pushd %SCRIPT_DIR%

where py >nul 2>&1
if errorlevel 1 (
    echo Python 3 is required but was not found. Please install Python 3 and rerun this script.
    pause
    exit /b 1
)

if not exist .venv (
    echo Creating isolated Python environment...
    py -3 -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -c "from vault.ui.icon_assets import ensure_icon_files; ensure_icon_files()"
set BUILD_DIR=dist\KakhasPasswordVault

pyinstaller --noconfirm --windowed ^
    --name "KakhasPasswordVault" ^
    --icon "vault\ui\generated\icon.ico" ^
    --add-data "vault\ui\styles.qss;vault\ui" ^
    main.py

if not exist %BUILD_DIR%\KakhasPasswordVault.exe (
    echo Build failed. Check the console output for details.
    pause
    exit /b 1
)

set DESKTOP=%USERPROFILE%\Desktop
if not exist "%DESKTOP%" (
    set DESKTOP=%USERPROFILE%
)

copy /Y "%BUILD_DIR%\KakhasPasswordVault.exe" "%DESKTOP%\Kakha's Password Vault.exe" >nul

echo Launching Kakha's Password Vault...
start "" "%DESKTOP%\Kakha's Password Vault.exe"

echo A desktop shortcut named "Kakha's Password Vault" has been created.
echo You can run the vault by double-clicking the shortcut any time.

popd
endlocal
