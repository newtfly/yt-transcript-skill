"""
transcript_watcher.py  —  YouTube transcript clipboard watcher
Sits in the system tray. When you copy a YouTube URL, it automatically
fetches the transcript and saves it to the transcripts/ folder.

Dependencies:  pip install pystray Pillow pyperclip
Run:           pythonw transcript_watcher.py   (no console window)
"""

import sys
import re
import time
import threading
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "pystray", "Pillow", "pyperclip", "--quiet"])
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw, ImageFont

try:
    import pyperclip
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip", "--quiet"])
    import pyperclip


# ── Config ────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
TRANSCRIPTS  = SCRIPT_DIR / "transcripts"
POLL_INTERVAL = 1.5          # seconds between clipboard checks
YOUTUBE_RE   = re.compile(r'(https?://(?:www\.)?(?:youtube\.com/watch\S+|youtu\.be/\S+))')


# ── State ─────────────────────────────────────────────────────────────
last_seen_url  = ""
active_jobs    = 0
tray_icon      = None


def make_icon(status="idle"):
    """Draw a simple tray icon. status: 'idle' | 'working'."""
    size = 64
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if status == "working":
        bg_color  = (255, 165, 0)   # orange = fetching
        dot_color = (255, 255, 255)
    else:
        bg_color  = (30, 120, 80)   # green = idle/ready
        dot_color = (255, 255, 255)

    # Circle background
    draw.ellipse([4, 4, size - 4, size - 4], fill=bg_color)
    # Play-button triangle (▶) as a simple marker
    draw.polygon([(22, 18), (22, 46), (46, 32)], fill=dot_color)
    return img


def notify(title, message):
    """Show a Windows toast notification via PowerShell (no extra deps)."""
    ps = (
        f'[void][System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms");'
        f'$n = New-Object System.Windows.Forms.NotifyIcon;'
        f'$n.Icon = [System.Drawing.SystemIcons]::Information;'
        f'$n.Visible = $true;'
        f'$n.ShowBalloonTip(4000, "{title}", "{message}", '
        f'[System.Windows.Forms.ToolTipIcon]::None);'
        f'Start-Sleep -Milliseconds 4500;'
        f'$n.Dispose()'
    )
    subprocess.Popen(
        ["powershell", "-WindowStyle", "Hidden", "-Command", ps],
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def fetch_transcript(url):
    global active_jobs, tray_icon

    active_jobs += 1
    if tray_icon:
        tray_icon.icon = make_icon("working")
        tray_icon.title = "Transcript Watcher — fetching…"

    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "yt_transcript.py"), url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            saved_path = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
            filename   = Path(saved_path).name if saved_path else "transcript"
            notify("✅ Transcript saved", filename)
        else:
            err = result.stderr.strip().splitlines()[-1] if result.stderr else "Unknown error"
            notify("❌ Transcript failed", err[:80])
    except subprocess.TimeoutExpired:
        notify("❌ Transcript timed out", url[:60])
    except Exception as e:
        notify("❌ Transcript error", str(e)[:80])
    finally:
        active_jobs -= 1
        if tray_icon and active_jobs == 0:
            tray_icon.icon  = make_icon("idle")
            tray_icon.title = "Transcript Watcher — ready"


def clipboard_loop():
    global last_seen_url
    while True:
        try:
            text = pyperclip.paste() or ""
            text = text.strip()
            match = YOUTUBE_RE.search(text)
            if match:
                url = match.group(1)
                if url != last_seen_url:
                    last_seen_url = url
                    notify("📋 YouTube URL detected", "Fetching transcript…")
                    threading.Thread(target=fetch_transcript, args=(url,), daemon=True).start()
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)


def open_transcripts_folder(icon, item):
    subprocess.Popen(["explorer", str(TRANSCRIPTS)])


def quit_app(icon, item):
    icon.stop()


def main():
    global tray_icon

    TRANSCRIPTS.mkdir(exist_ok=True)

    # Start clipboard monitor thread
    t = threading.Thread(target=clipboard_loop, daemon=True)
    t.start()

    # Build tray menu
    menu = pystray.Menu(
        item("Open transcripts folder", open_transcripts_folder),
        item("Quit", quit_app),
    )

    tray_icon = pystray.Icon(
        name="TranscriptWatcher",
        icon=make_icon("idle"),
        title="Transcript Watcher — ready",
        menu=menu,
    )
    tray_icon.run()


if __name__ == "__main__":
    main()
