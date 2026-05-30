@echo off
:: get_transcript.bat
:: ─────────────────────────────────────────────────────────────────────
:: HOW TO USE:
::   1. Copy a YouTube URL to your clipboard
::   2. Double-click this file
::   The transcript is saved to Maker_Projects\transcripts\ automatically.
:: ─────────────────────────────────────────────────────────────────────

setlocal

:: Get URL from clipboard
for /f "delims=" %%i in ('powershell -command "Get-Clipboard"') do set "YT_URL=%%i"

if "%YT_URL%"=="" (
    echo No URL found in clipboard.
    echo Copy a YouTube link first, then run this again.
    pause
    exit /b 1
)

:: Basic check — must contain youtube or youtu.be
echo %YT_URL% | findstr /i "youtube youtu.be" >nul
if errorlevel 1 (
    echo Clipboard doesn't look like a YouTube URL:
    echo   %YT_URL%
    echo Copy a YouTube link and try again.
    pause
    exit /b 1
)

echo.
echo Fetching transcript for:
echo   %YT_URL%
echo.

python "%~dp0yt_transcript.py" "%YT_URL%"

if errorlevel 1 (
    echo.
    echo Something went wrong. See error above.
    pause
    exit /b 1
)

echo.
echo Done! File saved to Maker_Projects\transcripts\
echo You can now ask Claude about it in Cowork or Claude Code.
echo.
pause
