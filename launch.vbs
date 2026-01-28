Set objShell = CreateObject("WScript.Shell")

' Use hardcoded path (adjust if needed)
strPath = "F:\src\whisper-dictation"
strPython = strPath & "\.venv\Scripts\python.exe"
strScript = strPath & "\src\main.py"

' Change to script directory
objShell.CurrentDirectory = strPath

' Run without visible console window (0 = hidden)
objShell.Run """" & strPython & """ """ & strScript & """", 0, False
