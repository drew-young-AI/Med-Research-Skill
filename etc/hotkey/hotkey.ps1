#!/usr/bin/env powershell

<#
.SYNOPSIS
    ?Ÿå??±éµè¼¸å…¥ç¨‹å? (Alt+P+P å¿«æ·??

.DESCRIPTION
    ä½¿ç”¨æ­¤è…³?¬å¯ä»¥å¿«?Ÿå??•è??¯ç†±?µç?å¼ï?ä¸¦æ?å®šè?è¼¸å…¥?„æ?å­—ã€?
    å¿«æ·?? Alt + P + P (??0.5 ç§’å…§????©æ¬¡ P)

.PARAMETER Text
    ?‡å?è¦è¼¸?¥ç??‡å? (?è¨­: 123456)

.EXAMPLE
    # ä½¿ç”¨?è¨­?‡å?
    .\hotkey.ps1

    # ?‡å??ªè??‡å?
    .\hotkey.ps1 -Text "ä½ å¥½ä¸–ç?"
    
    # ?–ç°¡å¯?
    .\hotkey.ps1 "ä½ å¥½ä¸–ç?"

#>

param(
    [Parameter(Position = 0, Mandatory = $false)]
    [string]$Text = "EatFood``12345"
)

# ?²å??³æœ¬?€?¨ç›®??
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptPath
$pythonScript = Join-Path $scriptPath "hotkey_sample.py"
$venvPython = Join-Path $repoRoot "dev\Scripts\python.exe"

# æª¢æŸ¥?›æ“¬?°å??¯å¦å­˜åœ¨
if (-not (Test-Path $venvPython)) {
    Write-Host "???±äº«?›æ“¬?°å?ä¸å??¨ï?è«‹å??¨å?æ¡ˆæ ¹?®é??·è?: python -m venv dev" -ForegroundColor Red
    exit 1
}

# æª¢æŸ¥ Python ?³æœ¬?¯å¦å­˜åœ¨
if (-not (Test-Path $pythonScript)) {
    Write-Host "??Python ?³æœ¬ä¸å??? $pythonScript" -ForegroundColor Red
    exit 1
}

# ?Ÿå? Python ç¨‹å?
Write-Host "??Activate..." -ForegroundColor Green
Write-Host "   Shortcut: Alt + P + P" -ForegroundColor Cyan
Write-Host ""

# ä½¿ç”¨?›æ“¬?°å?ä¸­ç? Python ?‹è??³æœ¬
& $venvPython $pythonScript $Text
