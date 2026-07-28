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

# Store the original location so we can return on cleanup
$OriginalLocation = Get-Location

# Track process objects for cleanup
$Processes = @()

function Stop-DevServers {
    Write-Host "`nShutting down dev servers..." -ForegroundColor $Red
    foreach ($process in $Processes) {
        if ($process -and -not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Set-Location $OriginalLocation
    Write-Host "All servers stopped." -ForegroundColor $Green
    exit 0
}

# Register cleanup for common interrupt signals
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-DevServers }

try {
    # Start Flask backend
    Write-Host "[Backend] Starting Flask on http://localhost:5000" -ForegroundColor $Green
    $FlaskProcess = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory $PSScriptRoot\.. -PassThru -NoNewWindow
    $Processes += $FlaskProcess

    # Start Next.js frontend
    Write-Host "[Frontend] Starting Next.js on http://localhost:3000" -ForegroundColor $Green
    $NextProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "$PSScriptRoot\..\frontend" -PassThru -NoNewWindow
    $Processes += $NextProcess

    Write-Host "Both servers running. Press Ctrl+C to stop." -ForegroundColor $Cyan

    # Wait for either process to exit
    $Exited = $null
    while ($Exited -eq $null) {
        $Exited = $Processes | Where-Object { $_.HasExited } | Select-Object -First 1
        if ($Exited) { break }
        Start-Sleep -Milliseconds 500
    }

    Write-Host "A server exited unexpectedly. Shutting down..." -ForegroundColor $Red
    Stop-DevServers
}
catch {
    Write-Host "Error: $_" -ForegroundColor $Red
    Stop-DevServers
}
