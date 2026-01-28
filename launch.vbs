Set objShell = CreateObject("WScript.Shell")
strPath = CreateObject("WScript.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
strPython = strPath & "\.venv\Scripts\python.exe"
strScript = strPath & "\src\main.py"

objShell.CurrentDirectory = strPath

' Run without visible console window (0 = hidden)
objShell.Run strPython & " " & strScript, 0, False
