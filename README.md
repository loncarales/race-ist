# race-ist
🎮 Race-ist ( Race Assist ) is a Python-based gesture control assistant for NFS Most Wanted that lets you race using only your hands, no controller needed!

```batch
# Go to your project folder
cd "C:\Users\Siddhant bali\OneDrive\Documents\race-ist"

# Create a virtual environment
python -m venv venv

# Activate the environment
.\venv\Scripts\activate

# Install packages cleanly inside venv
pip install opencv-python mediapipe pyautogui

```
pip install pyinstaller
pyinstaller --onefile --noconsole run.py
pyinstaller --onefile --noconsole --icon=raceassist.ico steering.py


pyinstaller --onefile --noconsole `
--icon=raceassist.ico `
--version-file=version.txt `
--add-data="venv\Lib\site-packages\mediapipe\modules:mediapipe\modules" `
run.py
