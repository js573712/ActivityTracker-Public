# Activity Tracker AI Instructions

## Project Overview
Windows-based activity tracker that silently logs active window titles to SQLite every 60 seconds, then uses Google Gemini API to generate categorized Markdown daily summaries. Data stays local until summarization.

## Architecture & Data Flow
1. [logger.py](../logger.py) - Polls `win32gui.GetForegroundWindow()` every 60s, only logs title changes to reduce DB size
2. [database.py](../database.py) - SQLite wrapper; stores `timestamp`, `date_str` (ISO format for easy grouping), `window_title`
3. [summarizer.py](../summarizer.py) - Fetches logs for date, sends to Gemini `gemini-2.5-flash`, saves Markdown to **parent directory** (not project root)

## Critical Patterns

### Database Schema
```python
activity_log: id, timestamp (auto-localtime), date_str (ISO), window_title
```
Query pattern: Always filter by `date_str`, sort by `timestamp ASC`

### Logger Deduplication
Logger only writes when `current_title != last_title`. Modify `POLL_INTERVAL_SECONDS` in [logger.py](../logger.py) to adjust frequency.

### Output Path Convention
Summaries save to `OUTPUT_DIR = os.path.dirname(os.path.dirname(__file__))` (parent directory), not project root. Format: `YYYY-MM-DD.md` or `YYYY-MM-DD_raw.txt` for `--raw` flag.

### Database Location
By default, `activity.db` saves to project directory. Customize via `.env`:
```env
DB_PATH=D:\Documents\ActivityLogs\activity.db
```
If unset, falls back to `<project_dir>/activity.db`. Useful for syncing DB to cloud storage or centralized log directory.

## Setup & Run Workflows

**Initial Setup:**
```bash
# Via install.bat (creates venv, installs deps, generates .env template)
install.bat

# Manual alternative
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
# Then create .env with GOOGLE_API_KEY=...
```

**Running:**
```bash
# Start logger (blocks console)
venv\Scripts\activate.bat && python logger.py

# Silent background via VBS (edit hardcoded paths first!)
run_logger_hidden.vbs

# Generate today's summary
venv\Scripts\activate.bat && python summarizer.py

# Specific date or export raw logs for local LLMs
python summarizer.py 2023-10-25
python summarizer.py --raw  # exports to parent dir as *_raw.txt
```

## Dependencies & Constraints
- **Windows-only**: Uses `win32gui` from `pywin32==311` for window detection
- **API Key Required**: Must set `GOOGLE_API_KEY` in `.env` (dotenv loaded in [summarizer.py](../summarizer.py))
- **LLM Flexibility**: Raw logs are yours; `--raw` flag enables feeding to local LLMs (Ollama, LM Studio) instead of Gemini

## Prompt Engineering & LLM Integration

### Customizing Gemini Prompts
The prompt in `generate_summary()` ([summarizer.py](../summarizer.py)) is the core categorization engine. Modify it for different use cases:

```python
# Default: General activity categorization
prompt = f"""Group my activities by category (e.g., Coding, Browsing, Communication, Research)..."""

# Project-focused: Track specific work
prompt = f"""Identify all activities related to Project X. Highlight context switches and deep work sessions..."""

# Time management: Analyze focus patterns
prompt = f"""Analyze time allocation. Flag distractions (social media, news sites). Calculate focused vs. fragmented work time..."""

# Privacy-preserving: Sanitize before sending
# Pre-process log_data to remove sensitive window titles before API call
log_data = sanitize_sensitive_titles(log_data)
```

### Alternative LLM Integration
Replace Gemini with local models to keep all data offline:

```bash
# Export raw logs
python summarizer.py --raw

# Feed to Ollama (example)
cat 2026-02-25_raw.txt | ollama run llama3 "Summarize these activity logs by category"

# Or integrate programmatically in summarizer.py:
import requests
response = requests.post('http://localhost:11434/api/generate',
    json={'model': 'llama3', 'prompt': prompt})
```

## Database Maintenance

### Backup Strategy
`activity.db.bak` is a manual backup checkpoint. Recommended practices:

```bash
# Before schema changes or bulk deletions
copy activity.db activity.db.bak

# Automated backup script (add to run_summarizer.bat or scheduled task)
python -c "import shutil; shutil.copy('activity.db', 'activity.db.bak')"
```

### Pruning Old Data
No auto-cleanup exists. To remove logs older than 90 days:

```python
# Add to database.py or run as script
conn = get_connection()
conn.execute("DELETE FROM activity_log WHERE date_str < date('now', '-90 days')")
conn.commit()
```

### Inspecting Data
```bash
# Quick stats
sqlite3 activity.db "SELECT date_str, COUNT(*) FROM activity_log GROUP BY date_str ORDER BY date_str DESC LIMIT 10"

# Export to CSV for analysis
sqlite3 -header -csv activity.db "SELECT * FROM activity_log" > export.csv
```

## Known TODOs (from codebase comments)
- Enhance activity detection beyond window titles (consider OCR on periodic screenshots, though token-intensive)
- Make intent capture more robust without compromising privacy/performance
