# YouTube Transcript Skill

Fetch and save YouTube video transcripts with a single click or command — no API key required.

## What it does

- Grabs the full transcript of any YouTube video (as long as captions are available)
- Saves it as a clean `.txt` file named with the date, video ID, and title slug
- Runs from the command line, a batch file double-click, or silently in the background via a system tray watcher

## Files

| File | Purpose |
|------|---------|
| `yt_transcript.py` | Core script — fetch and save a transcript |
| `transcript_watcher.py` | System tray app — auto-fetches whenever you copy a YouTube URL |
| `get_transcript.bat` | Double-click shortcut — reads URL from clipboard and runs the script |
| `install_watcher.bat` | One-time setup — installs the watcher to start automatically with Windows |
| `test_transcript.py` | Quick check that your setup is working |

## Requirements

```
pip install -r requirements.txt
```

Or install the core dependency only:

```
pip install youtube-transcript-api
```

The watcher also needs `pystray`, `Pillow`, and `pyperclip` (installed automatically by `install_watcher.bat`).

## Usage

**Command line:**
```
python yt_transcript.py https://youtu.be/VIDEOID
python yt_transcript.py VIDEOID --print
```

**Double-click:**
1. Copy a YouTube URL to your clipboard
2. Double-click `get_transcript.bat`
3. Transcript is saved to `transcripts/`

**Background watcher:**
1. Run `install_watcher.bat` once
2. After that, just copy any YouTube URL — transcript saves automatically, you get a Windows notification

## Output

Transcripts are saved to the `transcripts/` subfolder with names like:
```
20260528_dQw4w9WgXcQ_how-to-learn-anything-fast.txt
```

## Notes

- Works with standard YouTube URLs, short `youtu.be` links, Shorts, and raw video IDs
- Some videos have captions disabled — the script will tell you if that's the case
- No YouTube API key needed
