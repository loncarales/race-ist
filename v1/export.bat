@echo off
title 🔧 Building RaceAssist .exe
echo.
echo ========================================
echo   🧹 Cleaning up old build artifacts...
echo ========================================
taskkill /f /im run.exe >nul 2>&1
rmdir /s /q build
rmdir /s /q dist
del /f /q run.spec
echo ✔ Cleaned previous build.

echo.
echo ========================================
echo   🛠 Building RaceAssist...
echo ========================================

pyinstaller --onefile --noconsole --icon="raceassist.ico" --version-file="version.txt" ^
--add-data="venv\Lib\site-packages\mediapipe\modules;mediapipe\modules" ^
run.py

echo.
echo ========================================
echo   ✅ Build Complete! Output:
echo   dist\run.exe
echo ========================================
pause
