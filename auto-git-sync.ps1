# auto-git-sync.ps1
$ErrorActionPreference = "Continue"
$RepoPath = "D:\Repositories\Escherichia30636"
$LogFile   = "$RepoPath\auto-sync.log"
Set-Location $RepoPath

function Write-Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $msg"
    $line | Out-File -FilePath $LogFile -Append -Encoding utf8
}

Write-Log "======== START ========"

try {
    $pullResult = git pull --rebase 2>&1
    Write-Log "PULL: $pullResult"
} catch {
    Write-Log "PULL FAILED: $_"
}

$status = git status --porcelain
if ($status) {
    $addResult = git add -A 2>&1
    Write-Log "ADD: $addResult"

    $rawFiles = git diff --cached --name-only 2>&1
    $fileArray = @()
    if ($rawFiles) {
        $fileArray = @($rawFiles | Where-Object { $_ -and $_.Trim() -ne "" })
    }
    $fileCount = $fileArray.Count

    if ($fileCount -gt 0) {
        $names = @()
        foreach ($f in $fileArray) {
            $leaf = ($f -split '[\/]')[-1]
            if ($leaf) { $names += $leaf }
        }
        $shortNames = ($names -join ", ")
        if ($shortNames.Length -gt 80) {
            $shortNames = $shortNames.Substring(0, 80) + "..."
        }
        $dateStr = Get-Date -Format "yyyy-MM-dd HH:mm"
        $msg = "auto: sync $dateStr — $fileCount files: $shortNames"

        $commitResult = git commit -m $msg 2>&1
        Write-Log "COMMIT: $msg | $commitResult"

        try {
            $pushResult = git push 2>&1
            Write-Log "PUSH: $pushResult"
        } catch {
            Write-Log "PUSH FAILED: $_"
        }
    } else {
        Write-Log "SKIP: nothing staged after git add"
    }
} else {
    Write-Log "SKIP: no local changes"
}

Write-Log ""
