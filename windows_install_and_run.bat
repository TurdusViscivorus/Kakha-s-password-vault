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
set INSTALL_DIR=%LOCALAPPDATA%\KakhasPasswordVault

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

if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
)

mkdir "%INSTALL_DIR%"
xcopy "%BUILD_DIR%" "%INSTALL_DIR%" /E /I /Y >nul

if exist "%DESKTOP%\Kakha's Password Vault.lnk" (
    del "%DESKTOP%\Kakha's Password Vault.lnk"
)

powershell -NoProfile -Command ^
    "$WScript = New-Object -ComObject WScript.Shell;" ^
    "$Shortcut = $WScript.CreateShortcut('%DESKTOP%\Kakha''s Password Vault.lnk');" ^
    "$Shortcut.TargetPath = '%INSTALL_DIR%\KakhasPasswordVault.exe';" ^
    "$Shortcut.WorkingDirectory = '%INSTALL_DIR%';" ^
    "$Shortcut.IconLocation = '%INSTALL_DIR%\KakhasPasswordVault.exe,0';" ^
    "$Shortcut.Save()" >nul

echo Launching Kakha's Password Vault...
start "" "%INSTALL_DIR%\KakhasPasswordVault.exe"

echo Kakha's Password Vault has been installed to %INSTALL_DIR%.
echo A desktop shortcut named "Kakha's Password Vault" points to the installed app.

popd
endlocal
