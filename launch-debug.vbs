Set objShell = CreateObject("WScript.Shell")

' Use hardcoded path
strPath = "F:\src\whisper-dictation"
strPython = strPath & "\.venv\Scripts\python.exe"
strScript = strPath & "\src\main.py"

' Change to script directory
objShell.CurrentDirectory = strPath

' Show paths for debugging
MsgBox "Python: " & strPython & vbCrLf & "Script: " & strScript & vbCrLf & "Working dir: " & strPath

' Run with visible window for debugging
Dim objExec
Set objExec = objShell.Exec("""" & strPython & """ """ & strScript & """")

' Wait for it to finish or show error
If objExec.Status = 0 Then
    MsgBox "Application started successfully"
Else
    MsgBox "Error starting application: " & objExec.StdErr.ReadAll()
End If
