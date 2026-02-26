# Activity Tracker & Summarizer

This project is a Windows-based utility that silently logs the active window titles you interact with throughout the day into a local SQLite database. At the end of the day, it uses an AI/LLM (by default, the **Google Gemini API**) to generate a beautifully structured Markdown summary of your activities, grouped by inferred categories (e.g., Coding, Browsing, Communication) with a chronological timeline.

## Features
- **Silent Logging**: Runs in the background, logging active window titles every 60 seconds (configurable). Local database keeps your data completely private until summarization.
- **AI Daily Summaries**: Leverages Google's `gemini-2.5-flash` model out-of-the-box (or any LLM of your choice) to digest raw window logs and generate intelligent, categorized daily note summaries.
- **Markdown Output**: Automatically formats summaries as clean Markdown files, perfect for saving into systems like Obsidian, Notion, or purely as text files.

## Prerequisites
- **Operating System**: Windows (relies on `win32gui` for active window detection).
- **Python**: Python 3.8 or newer.
- **Google Gemini API Key**: You must have an active API key from Google AI Studio.

## Installation Instructions

### Automated Setup (Recommended)
1. **Clone or download** this exact repository to your local machine.
2. **Double-click** the `install.bat` file in the project folder. This script will automatically:
   - Verify Python is installed
   - Create an isolated virtual environment (`venv`)
   - Install all necessary dependencies from `requirements.txt`
   - Generate a placeholder `.env` file for your API key
3. **Open** the newly created `.env` file in a text editor and add your Google Gemini API key.
4. *(Optional)* If you plan to use the included helper scripts (`run_logger_hidden.vbs` and `run_summarizer.bat`), open them in a text editor and update the hardcoded paths to match the actual location of the repository.

---

### Manual Setup (Advanced)
If you prefer setting things up manually via the command line:

#### 1. Clone the Repository
```bash
git clone https://github.com/js573712/ActivityTracker-Public.git
cd ActivityTracker-Public
```

#### 2. Create a Virtual Environment
```bash
python -m venv venv
```
Activate the virtual environment:
- **Command Prompt**: `venv\Scripts\activate.bat`
- **PowerShell**: `venv\Scripts\Activate.ps1`

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Create a file named `.env` in the root directory with your settings:
```env
# Required: Your Google Gemini API key
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: How often to check for window changes (default: 60 seconds)
POLL_INTERVAL_SECONDS=60

# Optional: Custom database location (default: project directory)
DB_PATH=D:\Documents\ActivityLogs\activity.db
```

**Configuration Options:**
- `GOOGLE_API_KEY` (required) - Get this from [Google AI Studio](https://aistudio.google.com/apikey)
- `POLL_INTERVAL_SECONDS` (optional) - How many seconds between activity checks. Smaller = more frequent logging & larger DB. Default: 60
- `DB_PATH` (optional) - Save database to a cloud-synced folder or external drive. Default: project directory as `activity.db`

If not specified, the database saves to the project directory as `activity.db`. This is useful if you want to sync your activity logs to cloud storage or keep them in a centralized location.

### 5. Update Helper Scripts (If used)
The repository includes helper scripts (`run_logger_hidden.vbs` and `run_summarizer.bat`) to launch the scripts easily or silently.
**Important:** You must open these scripts in a text editor and update the hardcoded paths (`C:\Users\john.scott\...`) to match the actual path where you cloned the repository on your machine.

---

## Usage Guide

### 1. Start the Logger
To begin tracking your active windows, run the logger script:
```bash
python logger.py
```
*Tip: You can use the included `run_logger_hidden.vbs` to run the logger silently in the background without keeping a console window open.*

### 2. Generate Your Daily Summary
At the end of your day (or anytime you wish to summarize the logs for the current date), run the summarizer script:
```bash
python summarizer.py
```
This will fetch today's logs from the database, send them to Gemini for summarization, and save a Markdown file (e.g., `YYYY-MM-DD.md`) into the parent directory of this project.

You can also generate summaries for past dates by providing an ISO formatted date argument:
```bash
python summarizer.py 2023-10-25
```

## Updating

To update the project with the latest code and dependencies:

```bash
# Navigate to your project directory
cd ActivityTracker-Public

# Pull the latest changes from GitHub
git pull origin main

# Update Python dependencies
.\venv\Scripts\activate.bat
pip install -r requirements.txt --upgrade
```

If you used the automated `install.bat` setup, you can simply re-run it to refresh the virtual environment and dependencies.

## Extensibility & Configuration

The core of this application is a simple, private SQLite database. Because the raw data is completely yours, you can process the daily file with *any* AI/LLM you want.
- **Self-Hosted LLMs:** Don't want to use a cloud API? You can export the raw logs and feed them to a locally hosted model running on your machine (e.g., via Ollama or LM Studio) to ensure no data ever leaves your computer.
- **Alternative Exporting:** The data lives in `activity.db`. You can easily export it differently, like querying it to CSV or JSON, or feeding it into custom charting dashboards instead of using the default summarizer.
- **Custom Database Location:** Set `DB_PATH` in your `.env` file to save the database wherever you want (e.g., cloud-synced folder, external drive).

## Future Roadmap / TODOs

- **Richer Usage Information:** We need to gather more detailed usage information. For instance, using periodic screen grabs and performing OCR. While that might be token intensive to analyze, there might be other creative ways to synthesize that data.
- **Better Activity Detection:** The current method of telling "what the user is doing" solely by reading active window titles is rather rudimentary. We need a more robust way to capture true intent without compromising privacy or performance.
- **System Tray Application:** Convert to a Windows system tray daemon that runs silently in the background without requiring manual script execution.
- **Auto-Update Mechanism:** Implement update checking and automated updates via git pull and dependency refresh.

## Structure
- `logger.py` - Background logger that polls the active window title.
- `database.py` - SQLite helper functions for initializing the schema, inserting, and retrieving logs.
- `summarizer.py` - Script connecting to Gemini to summarize raw SQLite logs (includes a `--raw` flag to just export logs for other LLMs).
- `activity.db` - The local SQLite database generated by the script.
- `.github/copilot-instructions.md` - AI assistant guidance with implementation patterns, critical workflows, and architecture decisions. Used by GitHub Copilot and other AI coding assistants when modifying code.
