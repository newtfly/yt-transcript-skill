# YouTube Transcript Skill

Use this skill when the user provides a YouTube URL or video ID and wants to:
- Get a transcript of the video
- Summarize video content
- Extract ideas, workflows, or knowledge from a video
- Use video content as reference for building skills, agents, or workflows

## How to fetch the transcript

Run the companion Python script with the YouTube URL or video ID using the mcp__workspace__bash tool:

```bash
python "C:/Users/Dawne/OneDrive/Documents/Maker_Projects/yt-transcript-skill/yt_transcript.py" "<URL_OR_VIDEO_ID>"
```

The script outputs clean transcript text to stdout. Capture it and work with it directly.

**Example:**
```bash
python "C:/Users/Dawne/OneDrive/Documents/Maker_Projects/yt-transcript-skill/yt_transcript.py" "https://youtu.be/WIDIV8oDDC8"
```

The script accepts:
- Full YouTube URLs: `https://www.youtube.com/watch?v=...` or `https://youtu.be/...`
- Video IDs directly: `WIDIV8oDDC8`

## Step-by-step

1. Extract the URL or video ID from the user's message
2. Run the bash command above
3. Read stdout — it contains `# Transcript: <id>`, `# Segments: N`, then the full clean text
4. Proceed based on what the user wants (see below)

## After fetching

Once you have the transcript text:

1. **If the user wants a summary** — summarize the key ideas in clear prose
2. **If the user wants to extract workflows** — identify step-by-step processes and write them out
3. **If the user wants to build a skill/agent** — extract the core concept, propose a SKILL.md structure based on what the video teaches
4. **If the user wants to save it** — write the transcript to `C:\Users\Dawne\OneDrive\Documents\Maker_Projects\` with a filename like `transcript_<video_id>.txt`
5. **If the user wants to create a knowledge base** — organize extracted concepts into a structured markdown file

## Error handling

- **No transcript available**: Some videos disable captions. Tell the user and suggest a different video or manual paste.
- **Private/unavailable video**: Script will report this. Ask user to check the URL.
- **Library not installed**: Run `pip install youtube-transcript-api` then retry.
