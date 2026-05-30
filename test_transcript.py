"""
test_transcript.py — Quick verification that youtube-transcript-api works on this machine.
Run with:  python test_transcript.py
"""

import sys

# Step 1: check/install the library
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("✅ youtube-transcript-api already installed")
except ImportError:
    print("Installing youtube-transcript-api...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api"])
    from youtube_transcript_api import YouTubeTranscriptApi
    print("✅ Installed successfully")

# Step 2: fetch the transcript
VIDEO_ID = "WIDIV8oDDC8"
print(f"\nFetching transcript for video: {VIDEO_ID} ...")

try:
    api = YouTubeTranscriptApi()
    transcript = list(api.fetch(VIDEO_ID))
    print(f"✅ SUCCESS — got {len(transcript)} segments")
    print("\nFirst 5 segments:")
    for seg in transcript[:5]:
        print(f"  [{seg.start:.1f}s] {seg.text}")
    print("\n✅ The skill will work. You can delete this test file.")

except Exception as e:
    print(f"❌ FAILED: {e}")
    print("\nThis means the skill won't work with this approach.")
    print("Report this error back so we can find an alternative.")
