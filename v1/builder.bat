@echo off
setlocal enabledelayedexpansion
title 🚗 Building RaceAssist Installer...

:: ------------------------------
:: CONFIG
:: ------------------------------
set ENTRYPOINT=steering.py
set EXENAME=steering.exe
set ICON=installer\raceassist.ico
set VERSIONFILE=version.txt
set SPLASH=installer\splash.bmp
set SPLASH_SMALL=installer\splash_small.bmp
set README=installer\readme.txt
set OUTDIR=output

:: Kill existing exe
echo 🔄 Killing any running RaceAssist executable...
taskkill /f /im %EXENAME% >nul 2>&1

:: Clean build artifacts
echo 🧹 Cleaning previous build...
rmdir /s /q dist
rmdir /s /q build
del /f /q %EXENAME:.exe=.spec%

:: Build the .exe with PyInstaller
echo 🔧 Building standalone executable with PyInstaller...
pyinstaller --onefile --noconsole ^
--icon="%ICON%" ^
--version-file="%VERSIONFILE%" ^
"--add-data=venv\Lib\site-packages\mediapipe\modules;mediapipe\modules" ^
"--add-binary=venv\Lib\site-packages\cv2\opencv_videoio_ffmpeg*.dll;." ^
%ENTRYPOINT%

:: Create output dir
if not exist %OUTDIR% mkdir %OUTDIR%

:: Generate RaceAssist.iss
echo 📝 Generating installer script: RaceAssist.iss...
(
echo [Setup]
echo AppName=RaceAssist
echo AppVersion=1.0.0
echo AppPublisher=Siddhant Bali
echo DefaultDirName={autopf}^\\RaceAssist
echo DefaultGroupName=RaceAssist
echo UninstallDisplayIcon={app}^\\%EXENAME%
echo OutputDir=%OUTDIR%
echo OutputBaseFilename=RaceAssist Setup
echo SetupIconFile=%ICON%
echo Compression=lzma
echo SolidCompression=yes
echo WizardImageFile=%SPLASH%
echo WizardSmallImageFile=%SPLASH_SMALL%

echo.
echo [Files]
echo Source: "dist\%EXENAME%"; DestDir: "{app}"; Flags: ignoreversion
echo Source: "%README%"; DestDir: "{app}"; Flags: ignoreversion
echo Source: "venv\Lib\site-packages\cv2\opencv_videoio_ffmpeg*.dll"; DestDir: "{app}"; Flags: ignoreversion
echo Source: "venv\Lib\site-packages\mediapipe\modules\*"; DestDir: "{app}\mediapipe\modules"; Flags: recursesubdirs createallsubdirs

echo.
echo [Icons]
echo Name: "{group}\RaceAssist"; Filename: "{app}\%EXENAME%"
echo Name: "{userdesktop}\RaceAssist"; Filename: "{app}\%EXENAME%"; Tasks: desktopicon

echo.
echo [Tasks]
echo Name: "desktopicon"; Description: "Create a ^&desktop icon"; GroupDescription: "Additional icons:"

echo.
echo [Run]
echo Filename: "{app}\%EXENAME%"; Description: "Launch RaceAssist"; Flags: nowait postinstall skipifsilent
echo Filename: "notepad.exe"; Parameters: "{app}\readme.txt"; Description: "View Readme"; Flags: postinstall skipifsilent
) > RaceAssist.iss

:: Build installer using Inno Setup
echo 📦 Launching Inno Setup to build installer...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" RaceAssist.iss
) else (
    echo ❌ ERROR: Could not find Inno Setup compiler. Please install it from: https://jrsoftware.org/isinfo.php
    pause
    exit /b
)

echo ✅ Done! Find your installer at: %OUTDIR%\RaceAssist Setup.exe
pause
