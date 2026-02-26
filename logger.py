"""
TODO: better usage tracking
The current method of determining "what the user is doing" solely based on active window titles is rudimentary.
Consider adding a more robust method to capture intent (e.g., gathering richer context via periodic screen grabs and performing OCR).
Note that analyzing screen grabs might be token-intensive for LLMs, but there could be other creative ways to synthesize that data.
"""

import time
import os
import win32gui  # type: ignore
import database  # type: ignore
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(encoding='utf-8-sig')

# Configurable polling interval (in seconds) - set POLL_INTERVAL_SECONDS in .env to override
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

def get_active_window_title():
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        return title
    except Exception as e:
        print(f"Error getting window title: {e}")
        return ""

def main():
    database.init_db()
    print(f"[{datetime.now().isoformat()}] Logger started. Polling every {POLL_INTERVAL_SECONDS} seconds...")
    
    last_title = None
    
    try:
        while True:
            current_title = get_active_window_title()
            
            if current_title and current_title.strip() != "":
                # We only log if the title has changed from the last checked title to reduce db size.
                # You can change this to log every interval if preferred.
                if current_title != last_title:
                    database.log_activity(current_title)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Logged: {current_title}")
                    last_title = current_title
            else:
                last_title = ""
                
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nLogger stopped by user.")

if __name__ == "__main__":
    main()
