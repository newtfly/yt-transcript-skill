@echo off
:: install_watcher.bat
:: Sets up the transcript clipboard watcher and adds it to Windows startup.
:: Run this ONCE. After that, the watcher starts automatically with Windows.

setlocal
set "SCRIPT_DIR=%~dp0"
set "WATCHER=%SCRIPT_DIR%transcript_watcher.py"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP%\TranscriptWatcher.vbs"

echo.
echo === Transcript Watcher Setup ===
echo.

:: Install Python dependencies
echo Installing dependencies...
python -m pip install pystray Pillow pyperclip --quiet
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python is in your PATH.
    pause
    exit /b 1
)
echo   Dependencies installed.

:: Create a VBScript launcher (runs pythonw with no console window)
echo Creating startup launcher...
(
    echo Set WshShell = CreateObject("WScript.Shell"^)
    echo WshShell.Run "pythonw ""%WATCHER%""", 0, False
) > "%SHORTCUT%"

echo   Startup shortcut created.
echo.
echo === Done! ===
echo.
echo The watcher will now start automatically with Windows.
echo Starting it now for this session...
echo.

:: Launch it now without waiting
start "" /B pythonw "%WATCHER%"

echo Watcher is running in your system tray (look for the green circle icon^).
echo.
echo HOW TO USE:
echo   1. Copy any YouTube URL
echo   2. A notification appears: "Fetching transcript..."
echo   3. Another notification appears when done: filename saved
echo   4. Transcript is in: %SCRIPT_DIR%transcripts\
echo.
pause
