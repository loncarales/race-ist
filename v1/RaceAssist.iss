[Setup]
AppName=RaceAssist
AppVersion=1.0.0
AppPublisher=Siddhant Bali
DefaultDirName={autopf}\\RaceAssist
DefaultGroupName=RaceAssist
UninstallDisplayIcon={app}\\steering.exe
OutputDir=output
OutputBaseFilename=RaceAssist Setup
SetupIconFile=installer\raceassist.ico
Compression=lzma
SolidCompression=yes
WizardImageFile=installer\splash.bmp
WizardSmallImageFile=installer\splash_small.bmp

[Files]
Source: "dist\steering.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer\readme.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "venv\Lib\site-packages\cv2\opencv_videoio_ffmpeg.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "venv\Lib\site-packages\mediapipe\modules\*"; DestDir: "{app}\mediapipe\modules"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\RaceAssist"; Filename: "{app}\steering.exe"
Name: "{userdesktop}\RaceAssist"; Filename: "{app}\steering.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a ^&desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\steering.exe"; Description: "Launch RaceAssist"; Flags: nowait postinstall skipifsilent
Filename: "notepad.exe"; Parameters: "{app}\readme.txt"; Description: "View Readme"; Flags: postinstall skipifsilent
