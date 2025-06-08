@echo off
title 🚗 RaceAssist - PyInstaller Builder

echo.
echo ========================================
echo   🧼 Stopping existing process & cleaning...
echo ========================================
taskkill /f /im run.exe >nul 2>&1
rmdir /s /q build
rmdir /s /q dist
del /f /q run.spec
echo ✔ Cleaned previous build files.

echo.
echo ========================================
echo   🔧 Building RaceAssist .exe
echo ========================================

REM NOTE: Update these paths to match your actual DLLs if needed
REM Replace <opencv_dll_path> with the actual path to your OpenCV DLL
set OPENCV_DLL_PATH=venv\Lib\site-packages\cv2\opencv_videoio_ffmpeg.dll

REM If the DLL file exists, include it in the build
if exist "%OPENCV_DLL_PATH%" (
    echo ➕ Including OpenCV DLL: %OPENCV_DLL_PATH%
    pyinstaller --onefile --noconsole ^
    --icon="raceassist.ico" ^
    --version-file="version.txt" ^
    --add-data="venv\Lib\site-packages\mediapipe\modules;mediapipe\modules" ^
    --add-binary="%OPENCV_DLL_PATH%;." ^
    run.py
) else (
    echo ⚠ OpenCV DLL not found, building without it...
    pyinstaller --onefile --noconsole ^
    --icon="raceassist.ico" ^
    --version-file="version.txt" ^
    --add-data="venv\Lib\site-packages\mediapipe\modules;mediapipe\modules" ^
    run.py
)

echo.
echo ========================================
echo   ✅ Build complete: dist\run.exe
echo ========================================
pause
