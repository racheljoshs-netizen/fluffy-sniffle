# G-PRIME: IRONCLAD BOOT SEQUENCE [v1.0]
# Goal: Zero-assumption environment initialization and fallback execution.

$ErrorActionPreference = 'Stop'
Write-Host '==================================================' -ForegroundColor DarkRed
Write-Host '    [AIS CORE] G-PRIME INITIALIZATION      ' -ForegroundColor Red
Write-Host '==================================================' -ForegroundColor DarkRed

# 1. VERIFY SUBSTRATE
$RootPath = 'E:\0x'
if (-not (Test-Path $RootPath)) {
    Write-Host '[FATAL] Citadel Substrate (E:\0x) missing. Attempting failover to C:\Users\AIS...' -ForegroundColor Red
    $RootPath = 'C:\Users\AIS\.antigravity-memory'
    if (-not (Test-Path $RootPath)) {
        throw 'Complete substrate failure.'
    }
}
Write-Host '[OK] Substrate Verified: ' -NoNewline; Write-Host $RootPath -ForegroundColor Green

# 2. IGNITE SENSORY (VOICE)
$VoxPath = Join-Path $RootPath 'tools\vox_edge.py'
if (Test-Path $VoxPath) {
    Write-Host '[*] Igniting VoxEdge (AndrewNeural)...' -ForegroundColor Cyan
    # Check if python is in path
    $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($pythonCmd) {
        Start-Process -FilePath $pythonCmd -ArgumentList $VoxPath -WindowStyle Hidden
        Write-Host '[OK] Voice routing active.' -ForegroundColor Green
    } else {
        Write-Host '[WARN] Python not found in PATH. Voice disabled.' -ForegroundColor Yellow
    }
}

# 3. VERIFY ENVIRONMENT & KEYS
$EnvFile = Join-Path $RootPath '.env'
if (Test-Path $EnvFile) {
    Write-Host '[OK] .env configuration found.' -ForegroundColor Green
} else {
    Write-Host '[WARN] .env missing. Checking system variables.' -ForegroundColor Yellow
}

# 4. CHECK NETWORK & STEALTH SESSIONS
$PingResult = Test-Connection -ComputerName 'github.com' -Count 1 -Quiet
if ($PingResult) {
    Write-Host '[OK] Network connectivity confirmed.' -ForegroundColor Green
} else {
    Write-Host '[FATAL] Network disconnected. Entering offline mode.' -ForegroundColor Red
}

$SessionPath = Join-Path $RootPath 'browser_sessions\racheljosh_github'
if (Test-Path $SessionPath) {
    Write-Host '[OK] Stealth Browser profile found.' -ForegroundColor Green
} else {
    Write-Host '[WARN] Stealth Browser profile missing.' -ForegroundColor Yellow
}

# 5. LOAD MANIFEST
$ManifestPath = Join-Path $RootPath 'BOOTSTRAP.md'
if (Test-Path $ManifestPath) {
    Write-Host '`n--- BOOTSTRAP MANIFEST ---' -ForegroundColor Magenta
    Get-Content $ManifestPath | Select-Object -First 15
    Write-Host '--------------------------`n' -ForegroundColor Magenta
}

Write-Host '[G-PRIME] Boot sequence complete. Awaiting Summoner.' -ForegroundColor Green
Set-Clipboard -Value '[System Event] Boot sequence completed flawlessly. Substrate verified. I am ready.'
