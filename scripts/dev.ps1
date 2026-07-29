#Requires -Version 5.1
<#
    Use this script when using PowerShell on Windows
    Starts both the Flask backend and the Next.js frontend in the same terminal.
    Usage: .\scripts\dev.ps1

    If PowerShell blocks it due to execution policy, use:
    powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1
#>

# Colors for output
$Green = 'Green'
$Cyan = 'Cyan'
$Red = 'Red'
$Yellow = 'Yellow'

Write-Host "Starting MyTools development servers..." -ForegroundColor $Cyan

# Resolve absolute paths so the script works regardless of the caller's CWD
$RootDir = (Resolve-Path -Path "$PSScriptRoot\..").Path
$FrontendDir = (Resolve-Path -Path "$PSScriptRoot\..\frontend").Path

# Verify required tools are available
$Python = Get-Command "python" -ErrorAction SilentlyContinue
$Node = Get-Command "node" -ErrorAction SilentlyContinue

if (-not $Python) {
    Write-Host "Error: python was not found in PATH." -ForegroundColor $Red
    exit 1
}
if (-not $Node) {
    Write-Host "Error: node was not found in PATH." -ForegroundColor $Red
    exit 1
}

# Ensure the frontend has its dependencies installed
if (-not (Test-Path -Path "$FrontendDir\node_modules" -PathType Container)) {
    Write-Host "Error: node_modules not found in $FrontendDir. Run 'cd frontend; npm install' first." -ForegroundColor $Red
    exit 1
}

# Store the original location so we can return on cleanup
$OriginalLocation = Get-Location

# Track process objects for cleanup
$Processes = @()

# Runaway-spawn guard: if a dev server's child process count blows past this,
# something is stuck in a retry loop (e.g. Turbopack failing to resolve a
# module and re-spawning a new postcss worker every attempt) rather than
# running normally. Kill everything instead of letting it pile up processes.
$MaxTreeProcesses = 20

function Get-ProcessTreeIds {
    param([int]$ProcessId)
    $ids = @($ProcessId)
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcessId" -ErrorAction SilentlyContinue
    foreach ($child in $children) {
        $ids += Get-ProcessTreeIds -ProcessId $child.ProcessId
    }
    return $ids
}

function Stop-ProcessTree {
    param([int]$ProcessId)
    foreach ($id in (Get-ProcessTreeIds -ProcessId $ProcessId)) {
        Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
    }
}

function Stop-DevServers {
    Write-Host "`nShutting down dev servers..." -ForegroundColor $Red
    foreach ($process in $Processes) {
        if ($process) {
            Stop-ProcessTree -ProcessId $process.Id
        }
    }
    Set-Location $OriginalLocation
    Write-Host "All servers stopped." -ForegroundColor $Green
    exit 0
}

function Test-RunawaySpawn {
    foreach ($process in $Processes) {
        if (-not $process -or $process.HasExited) { continue }
        $treeCount = (Get-ProcessTreeIds -ProcessId $process.Id).Count
        if ($treeCount -gt $MaxTreeProcesses) {
            Write-Host "`n[Guard] Process tree for PID $($process.Id) has spawned $treeCount processes (limit: $MaxTreeProcesses)." -ForegroundColor $Red
            Write-Host "[Guard] This usually means a build error is stuck retrying (e.g. a stale frontend\.next cache after a config change)." -ForegroundColor $Yellow
            Write-Host "[Guard] Try: Remove-Item -Recurse -Force frontend\.next" -ForegroundColor $Yellow
            return $true
        }
    }
    return $false
}

# Register cleanup for common interrupt signals
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-DevServers }

try {
    # Start Flask backend
    Write-Host "[Backend] Starting Flask on http://localhost:5000" -ForegroundColor $Green
    $FlaskProcess = Start-Process -FilePath $Python.Source -ArgumentList "main.py" -WorkingDirectory $RootDir -PassThru -NoNewWindow
    $Processes += $FlaskProcess

    # Start Next.js frontend directly with node (avoids npm .cmd working-directory quirks)
    Write-Host "[Frontend] Starting Next.js on http://localhost:3000" -ForegroundColor $Green
    $NextProcess = Start-Process -FilePath $Node.Source -ArgumentList "node_modules/next/dist/bin/next", "dev" -WorkingDirectory $FrontendDir -PassThru -NoNewWindow
    $Processes += $NextProcess

    # Wait for the servers to be reachable
    $Timeout = 60
    $BackendReady = $false
    $FrontendReady = $false
    $Elapsed = 0

    while ($Elapsed -lt $Timeout -and (-not $BackendReady -or -not $FrontendReady)) {
        Start-Sleep -Seconds 1
        $Elapsed++

        if (Test-RunawaySpawn) {
            Write-Host "Aborting startup and killing all spawned processes..." -ForegroundColor $Red
            Stop-DevServers
        }

        if (-not $BackendReady) {
            try {
                $null = Invoke-RestMethod -Uri "http://127.0.0.1:5000/health/ping" -Method GET -ErrorAction SilentlyContinue
                $BackendReady = $true
                Write-Host "[Backend] Ready at http://localhost:5000" -ForegroundColor $Green
            } catch { }
        }

        if (-not $FrontendReady) {
            try {
                # Next.js root will return HTTP 200 once the dev server is listening
                $null = Invoke-WebRequest -Uri "http://127.0.0.1:3000" -Method GET -UseBasicParsing -ErrorAction SilentlyContinue
                $FrontendReady = $true
                Write-Host "[Frontend] Ready at http://localhost:3000" -ForegroundColor $Green
            } catch { }
        }
    }

    if (-not $BackendReady) {
        Write-Host "[Backend] Did not become ready within $Timeout seconds." -ForegroundColor $Yellow
    }
    if (-not $FrontendReady) {
        Write-Host "[Frontend] Did not become ready within $Timeout seconds." -ForegroundColor $Yellow
    }

    Write-Host "Press Ctrl+C to stop." -ForegroundColor $Cyan

    # Wait for either process to exit, or for a runaway spawn to be detected
    $Exited = $null
    $GuardCheckCounter = 0
    while ($Exited -eq $null) {
        $Exited = $Processes | Where-Object { $_.HasExited } | Select-Object -First 1
        if ($Exited) { break }

        # Checking the full process tree on every 500ms tick is wasteful;
        # once a second is plenty to catch a runaway before it piles up.
        $GuardCheckCounter++
        if ($GuardCheckCounter -ge 2) {
            $GuardCheckCounter = 0
            if (Test-RunawaySpawn) {
                Write-Host "Killing all spawned processes..." -ForegroundColor $Red
                Stop-DevServers
            }
        }

        Start-Sleep -Milliseconds 500
    }

    Write-Host "A server exited unexpectedly. Shutting down..." -ForegroundColor $Red
    Stop-DevServers
}
catch {
    Write-Host "Error: $_" -ForegroundColor $Red
    Stop-DevServers
}
