"""
yt_transcript.py  —  Fetch a YouTube video transcript and save to transcripts/ folder.

Usage:
    python yt_transcript.py <YouTube URL or video ID>
    python yt_transcript.py <YouTube URL or video ID> --print   # print to stdout instead of saving

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


def main():
    if len(sys.argv) < 2:
        print("Usage: python yt_transcript.py <YouTube URL or video ID>", file=sys.stderr)
        sys.exit(1)

    raw = sys.argv[1]
    print_mode = "--print" in sys.argv
    video_id = extract_video_id(raw)

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
    header = f"# Title: {title or 'Unknown'}\n# Video ID: {video_id}\n# URL: https://www.youtube.com/watch?v={video_id}\n# Date fetched: {date_str}\n# Segments: {len(segments)}\n\n"
    output = header + text + "\n"

    if print_mode:
        print(output)
        return

    # Save to transcripts folder
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)
    filename = f"{date_str}_{video_id}_{slug}.txt"
    out_path = TRANSCRIPTS_DIR / filename
    out_path.write_text(output, encoding="utf-8")

    print(f"\n✅ Saved: transcripts/{filename}", file=sys.stderr)
    print(f"   Title:    {title or 'Unknown'}", file=sys.stderr)
    print(f"   Segments: {len(segments)}", file=sys.stderr)
    print(str(out_path))  # stdout: just the path, for scripts to capture


if __name__ == "__main__":
    main()
