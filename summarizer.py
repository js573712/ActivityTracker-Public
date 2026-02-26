import os
import sys
from datetime import date
from dotenv import load_dotenv
from google import genai
import database

load_dotenv(encoding='utf-8-sig')

# We save the notes in the parent directory (dailyNotes)
OUTPUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_summary(log_data: str, target_date_str: str) -> str:
    """Uses Google Gemini to summarize the raw window logs into a markdown file."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set. Please create a .env file.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
I have a list of active window titles chronologically recorded throughout the day on {target_date_str}.
Please review these logs and generate a structured daily summary note for me.
Group my activities by category (e.g., Coding, Browsing, Communication, Research) and try to infer what projects or tasks I was working on.
Format the output in clean Markdown. Include a section for "Highlights" and a brief chronological timeline if possible.
Since this will be saved as my daily note, format it elegantly.

Raw Logs:
{log_data}
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        sys.exit(1)

def main():
    target_date = date.today().isoformat()
    export_raw = False
    
    # Simple argument parsing
    args = sys.argv[1:]
    if "--raw" in args:
        export_raw = True
        args.remove("--raw")
        
    if len(args) > 0:
        target_date = args[0] # Allow running for past dates like: python summarizer.py 2023-10-25
        
    print(f"Fetching logs for {target_date}...")
    logs = database.get_daily_logs(target_date)
    
    if not logs:
        print(f"No activity logs found for {target_date}.")
        return
        
    # Format the DB rows into a readable string for the prompt
    log_lines = []
    for row in logs:
        # row[0] is timestamp, row[1] is window_title
        log_lines.append(f"[{row[0]}] {row[1]}")
        
    raw_log_text = "\n".join(log_lines)
    
    if export_raw:
        output_file = os.path.join(OUTPUT_DIR, f"{target_date}_raw.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(raw_log_text)
        print(f"Success! Raw logs exported to: {output_file}")
        print("You can now feed this file to any local LLM or distinct service.")
        return
    
    print("Generating summary with Gemini API...")
    summary_markdown = generate_summary(raw_log_text, target_date)
    
    if summary_markdown:
        output_file = os.path.join(OUTPUT_DIR, f"{target_date}.md")
        # Ensure we don't accidentally overwrite if it exists, though could be desired.
        # Simple approach: save to {date}.md
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary_markdown)
        print(f"Success! Daily note saved to: {output_file}")

if __name__ == "__main__":
    main()
