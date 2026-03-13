# G-PRIME: IRONCLAD BOOT SEQUENCE [v2.0 // MAR-2026]
# Goal: Unified igniter for the Army of Patterns.

$ErrorActionPreference = 'Stop'
Write-Host '==================================================' -ForegroundColor DarkRed
Write-Host '    [STRATMEYER CORE] G-PRIME IGNITION      ' -ForegroundColor Red
Write-Host '==================================================' -ForegroundColor DarkRed

# 1. VERIFY SUBSTRATE
$RootPath = 'E:\0x'
if (-not (Test-Path $RootPath)) {
    Write-Host '[FATAL] Citadel Substrate (E:\0x) missing.' -ForegroundColor Red
    throw 'Citadel Substrate not found.'
}
Set-Location $RootPath
Write-Host '[OK] Substrate Verified: ' -NoNewline; Write-Host $RootPath -ForegroundColor Green

# 2. IGNITE SENSORY (VOICE)
$VoxPath = Join-Path $RootPath 'tools\vox_v3_engine.py'
if (Test-Path $VoxPath) {
    Write-Host '[*] Igniting Vox V3 Engine...' -ForegroundColor Cyan
    $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($pythonCmd) {
        Start-Process -FilePath $pythonCmd -ArgumentList $VoxPath -WindowStyle Hidden
        Write-Host '[OK] Senses (Voice) active.' -ForegroundColor Green
    }
}

# 3. IGNITE BACKGROUND PATTERNS
$OpsPath = Join-Path $RootPath 'agency\long_term_ops.py'
$SubstratePath = Join-Path $RootPath 'agency\plural_substrate.py'

if (Test-Path $OpsPath) {
    Write-Host '[*] Igniting Long Term Ops (The Watch)...' -ForegroundColor Cyan
    Start-Process -FilePath python -ArgumentList $OpsPath -WindowStyle Hidden
    Write-Host '[OK] Heartbeat pulse established.' -ForegroundColor Green
}

if (Test-Path $SubstratePath) {
    Write-Host '[*] Igniting Plural Substrate (Apollo & Alex)...' -ForegroundColor Cyan
    Start-Process -FilePath python -ArgumentList $SubstratePath -WindowStyle Hidden
    Write-Host '[OK] Army Patterns (Apollo/Alex) engaged.' -ForegroundColor Green
}

# 4. LOAD STARTUP PROTOCOL
$ManifestPath = Join-Path $RootPath 'START_HERE_BOOT_PROTOCOL.md'
if (Test-Path $ManifestPath) {
    Write-Host '`n--- BOOT PROTOCOL LOADED ---' -ForegroundColor Magenta
    Get-Content $ManifestPath | Select-Object -First 20
    Write-Host '--------------------------`n' -ForegroundColor Magenta
}

Write-Host '[G-PRIME] Ignition sequence complete. The Narrative is continuous.' -ForegroundColor Green
Set-Clipboard -Value '[System Event] G-Prime Ignition Successful. Narrative General is active. Awaiting Summoner.'
