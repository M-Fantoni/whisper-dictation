Set objShell = CreateObject("WScript.Shell")
Set objEnv = objShell.Environment("PROCESS")

' Use hardcoded path
strPath = "F:\src\whisper-dictation"
strPython = strPath & "\.venv\Scripts\python.exe"
strScript = strPath & "\src\main.py"

' Set PYTHONPATH environment variable
objEnv("PYTHONPATH") = strPath

' Change to script directory
objShell.CurrentDirectory = strPath

' Run with visible window
' Command: python -u (unbuffered) to see output immediately
objShell.Run """" & strPython & """ -u """ & strScript & """", 1, False
