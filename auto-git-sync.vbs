' auto-git-sync.vbs — 完全无窗口启动 PowerShell 脚本
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ""D:\Repositories\Escherichia30636\auto-git-sync.ps1""", 0, False
Set WshShell = Nothing
