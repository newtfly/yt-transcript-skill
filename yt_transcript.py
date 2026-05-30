"""
yt_transcript.py  —  Fetch a YouTube video transcript and save to transcripts/ folder.

Usage:
    python yt_transcript.py <YouTube URL or video ID>
    python yt_transcript.py <YouTube URL or video ID> --print   # print to stdout instead of saving
    python yt_transcript.py --list                              # show all saved transcripts

Output filename format:
    YYYYMMDD_<video_id>_<slugified-title>.txt
    e.g. 20260528_WIDIV8oDDC8_agentic-engineering-workflow.txt
"""

import sys
import re
import json
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path


TRANSCRIPTS_DIR = Path(__file__).parent / "transcripts"


def extract_video_id(url_or_id: str) -> str:
    m = re.search(r'youtu\.be/([A-Za-z0-9_-]{11})', url_or_id)
    if m:
        return m.group(1)
    m = re.search(r'[?&]v=([A-Za-z0-9_-]{11})', url_or_id)
    if m:
        return m.group(1)
    m = re.search(r'(?:shorts|embed)/([A-Za-z0-9_-]{11})', url_or_id)
    if m:
        return m.group(1)
    if re.match(r'^[A-Za-z0-9_-]{11}$', url_or_id.strip()):
        return url_or_id.strip()
    return url_or_id.strip()


def get_video_title(video_id: str) -> str:
    """Fetch video title via YouTube oEmbed API (no API key required)."""
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get("title", "")
    except Exception:
        return ""


def slugify(text: str) -> str:
    """Convert title to a clean filename-safe slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60]  # cap length


def find_existing(video_id: str):
    """Check if a transcript for this video ID already exists. Returns Path or None."""
    if not TRANSCRIPTS_DIR.exists():
        return None
    for f in TRANSCRIPTS_DIR.glob(f"*_{video_id}_*.txt"):
        return f  # return the first match
    return None


def read_title_from_file(path: Path) -> str:
    """Read the title line from a saved transcript file."""
    try:
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        return first_line.replace("# Title: ", "").strip()
    except Exception:
        return path.stem


def list_transcripts():
    """Print a readable list of all saved transcripts."""
    if not TRANSCRIPTS_DIR.exists() or not any(TRANSCRIPTS_DIR.glob("*.txt")):
        print("\n No transcripts saved yet.\n")
        return

    files = sorted(
        [f for f in TRANSCRIPTS_DIR.glob("*.txt") if f.name != "CLAUDE.md"],
        reverse=True  # newest first
    )

    print(f"\n Your saved transcripts ({len(files)} total):\n")
    print(f"  {'#':<4} {'Date':<12} {'Title':<55} {'Video ID'}")
    print(f"  {'-'*4} {'-'*12} {'-'*55} {'-'*11}")

    for i, f in enumerate(files, 1):
        # Parse date and video ID from filename: YYYYMMDD_VIDEOID_slug.txt
        parts = f.stem.split("_", 2)
        if len(parts) >= 2:
            raw_date = parts[0]
            video_id = parts[1]
            try:
                date_str = f"{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
            except Exception:
                date_str = raw_date
        else:
            date_str = "Unknown"
            video_id = "Unknown"

        title = read_title_from_file(f)
        title_display = title[:53] + ".." if len(title) > 55 else title
        print(f"  {i:<4} {date_str:<12} {title_display:<55} {video_id}")

    print()


def main():
    # Handle --list flag
    if "--list" in sys.argv:
        list_transcripts()
        return

    if len(sys.argv) < 2:
        print("Usage:", file=sys.stderr)
        print("  python yt_transcript.py <YouTube URL or video ID>", file=sys.stderr)
        print("  python yt_transcript.py --list   (see all saved transcripts)", file=sys.stderr)
        sys.exit(1)

    raw = sys.argv[1]
    print_mode = "--print" in sys.argv
    video_id = extract_video_id(raw)

    # ── Duplicate check ───────────────────────────────────────────────
    if not print_mode:
        existing = find_existing(video_id)
        if existing:
            title = read_title_from_file(existing)
            parts = existing.stem.split("_", 2)
            raw_date = parts[0] if parts else "Unknown"
            try:
                date_str = f"{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
            except Exception:
                date_str = raw_date

            print(f"\nWARNING:  You already have this transcript!", file=sys.stderr)
            print(f"   Title:    {title}", file=sys.stderr)
            print(f"   Saved:    {date_str}", file=sys.stderr)
            print(f"   File:     transcripts/{existing.name}", file=sys.stderr)
            print(f"\n   To fetch a fresh copy anyway, add --force to your command.", file=sys.stderr)
            print(f"   To see all your transcripts, run: python yt_transcript.py --list\n", file=sys.stderr)

            if "--force" not in sys.argv:
                print(str(existing))  # stdout: return existing path for scripts
                sys.exit(0)

            print(f"   --force detected. Fetching a fresh copy...\n", file=sys.stderr)

    # ── Fetch transcript ──────────────────────────────────────────────
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("ERROR: youtube-transcript-api not installed.", file=sys.stderr)
        print("Run: pip install youtube-transcript-api", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching transcript for {video_id}...", file=sys.stderr)
    try:
        api = YouTubeTranscriptApi()
        segments = list(api.fetch(video_id))
    except Exception as e:
        print(f"ERROR: Could not fetch transcript for '{video_id}': {e}", file=sys.stderr)
        sys.exit(1)

    # Build clean text
    text = " ".join(seg.text.strip() for seg in segments)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Fetch title
    print("Fetching video title...", file=sys.stderr)
    title = get_video_title(video_id)
    slug = slugify(title) if title else "untitled"

    # Build output
    date_str = datetime.now().strftime("%Y%m%d")
    header = (
        f"# Title: {title or 'Unknown'}\n"
        f"# Video ID: {video_id}\n"
        f"# URL: https://www.youtube.com/watch?v={video_id}\n"
        f"# Date fetched: {date_str}\n"
        f"# Segments: {len(segments)}\n\n"
    )
    output = header + text + "\n"

    if print_mode:
        print(output)
        return

    # Save to transcripts folder
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)
    filename = f"{date_str}_{video_id}_{slug}.txt"
    out_path = TRANSCRIPTS_DIR / filename
    out_path.write_text(output, encoding="utf-8")

    print(f"\nOK Saved: transcripts/{filename}", file=sys.stderr)
    print(f"   Title:    {title or 'Unknown'}", file=sys.stderr)
    print(f"   Segments: {len(segments)}", file=sys.stderr)
    print(str(out_path))  # stdout: just the path, for scripts to capture


if __name__ == "__main__":
    main()
