---
name: testing-youtube-agent
description: Test the YouTube Agent IA CLI pipeline end-to-end. Use when verifying video creation, script generation, or TTS changes.
---

# Testing YouTube Agent IA

## Prerequisites

- Python 3.11+ with `uv` package manager
- FFmpeg installed (`sudo apt install ffmpeg`)
- Dependencies installed (`uv sync`)

## Devin Secrets Needed

- `GROQ_API_KEY` — Free API key from https://console.groq.com/keys (required for text generation)
- `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` — From Google Cloud Console (only needed for upload testing)

## Environment Setup

```bash
cd /home/ubuntu/repos/youtube-agent-ia
uv sync
cp .env.example .env
# Fill in GROQ_API_KEY in .env
```

## CLI Commands Available

| Command | What it tests |
|---------|---------------|
| `youtube-agent research --count N --niche "topic"` | Groq API + JSON parsing |
| `youtube-agent script --title "X" --description "Y"` | Script generation + JSON structure |
| `youtube-agent create --no-upload` | Full pipeline (research → script → TTS → images → video) |
| `youtube-agent create --niche "X" --no-upload` | Full pipeline with specific niche |
| `youtube-agent batch --count N --no-upload` | Multiple video creation |

## Key Verification Points

After running `youtube-agent create --no-upload`, verify:

1. **Output directory** created under `./output/` with timestamp prefix
2. **script.json** — Valid JSON with keys: title, description, tags, sections, thumbnail_text
3. **audio/section_*.mp3** — One per section, each > 10KB
4. **images/section_*.png** — One per section, each 1920x1080
5. **thumbnail.png** — 1280x720
6. **final_video.mp4** — Use `ffprobe` to verify:
   - 2 streams (video h264 + audio aac)
   - Resolution: 1920x1080
   - Duration > 10 seconds

```bash
ffprobe -v error -show_format -show_streams output/<dir>/final_video.mp4 2>&1 | grep -E 'codec_type|codec_name|width|height|duration=|nb_streams'
```

## Spanish Content Verification

Check that generated content is in Spanish:
```bash
python3 -c "
import json
s = json.load(open('output/<dir>/script.json'))
for sec in s['sections']:
    narr = sec['narration']
    has_spanish = any(w in narr.lower() for w in ['es', 'que', 'los', 'para', 'del'])
    print(f'{sec[\"section_title\"]}: spanish={has_spanish}')
"
```

## Known Limitations

- **YouTube upload** requires browser-based OAuth2 flow — cannot test in headless environments. First run opens browser for authorization, saves `token.json` for subsequent runs.
- **Video assembly** takes ~10-12 minutes depending on section count (MoviePy encoding).
- **Groq rate limits**: Free tier allows 30 req/min. If testing batch mode with many videos, may hit rate limits.
- **Error handling**: Missing/invalid API key produces a raw Python traceback instead of a user-friendly message.
- **Gemini API**: May not work in some Latin American regions (free tier quota shows as 0). Groq is the recommended alternative.
