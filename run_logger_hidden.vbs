Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c ""cd /d C:\path\to\your\ActivityTracker && venv\Scripts\activate.bat && pythonw logger.py""", 0, False
