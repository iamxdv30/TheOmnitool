<#
.SYNOPSIS
    Docker PostgreSQL management script for Windows

.DESCRIPTION
    Manages the local PostgreSQL Docker container for development.
    Provides commands to start, stop, reset, and interact with the database.

.PARAMETER Command
    The action to perform: start, stop, reset, logs, shell, status

.EXAMPLE
    .\scripts\docker-db.ps1 start
    Starts the PostgreSQL container

.EXAMPLE
    .\scripts\docker-db.ps1 reset
    Destroys all data and recreates the container

.EXAMPLE
    .\scripts\docker-db.ps1 shell
    Opens a PostgreSQL shell (psql)
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet("start", "stop", "reset", "logs", "shell", "status")]
    [string]$Command
)

$ErrorActionPreference = "Stop"
$ContainerName = "omnitool-postgres"
$MaxRetries = 30
$RetryInterval = 1

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    switch ($Type) {
        "Success" { Write-Host "[OK] $Message" -ForegroundColor Green }
        "Error"   { Write-Host "[ERROR] $Message" -ForegroundColor Red }
        "Warning" { Write-Host "[WARN] $Message" -ForegroundColor Yellow }
        default   { Write-Host "[INFO] $Message" -ForegroundColor Cyan }
    }
}

function Test-DockerRunning {
    try {
        $null = docker info 2>&1
        return $true
    } catch {
        return $false
    }
}

function Wait-ForPostgres {
    Write-Host "Waiting for PostgreSQL to be ready..."
    $retries = 0
    while ($retries -lt $MaxRetries) {
        $result = docker exec $ContainerName pg_isready -U omnitool -d omnitool_dev 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        $retries++
        Write-Host "  Attempt $retries/$MaxRetries..."
        Start-Sleep -Seconds $RetryInterval
    }
    return $false
}

# Check Docker is running
if (-not (Test-DockerRunning)) {
    Write-Status "Docker is not running. Please start Docker Desktop." "Error"
    exit 1
}

switch ($Command) {
    "start" {
        Write-Status "Starting PostgreSQL container..."

        # Check if container already running
        $running = docker ps --filter "name=$ContainerName" --format "{{.Names}}" 2>&1
        if ($running -eq $ContainerName) {
            Write-Status "PostgreSQL is already running" "Warning"
            exit 0
        }

        # Start container
        docker-compose up -d postgres

        if (Wait-ForPostgres) {
            Write-Status "PostgreSQL is ready on localhost:5432" "Success"
            Write-Host ""
            Write-Host "Connection Details:"
            Write-Host "  Host:     localhost"
            Write-Host "  Port:     5432"
            Write-Host "  Database: omnitool_dev"
            Write-Host "  User:     omnitool"
            Write-Host "  Password: omnitool_dev"
            Write-Host ""
            Write-Host "Connection URL:"
            Write-Host "  postgresql://omnitool:omnitool_dev@localhost:5432/omnitool_dev"
        } else {
            Write-Status "PostgreSQL failed to start within timeout" "Error"
            Write-Host "Check logs with: .\scripts\docker-db.ps1 logs"
            exit 1
        }
    }

    "stop" {
        Write-Status "Stopping PostgreSQL container..."
        docker-compose stop postgres
        Write-Status "PostgreSQL stopped (data preserved)" "Success"
    }

    "reset" {
        Write-Status "Resetting PostgreSQL (ALL DATA WILL BE LOST)..." "Warning"

        $confirmation = Read-Host "Are you sure? Type 'yes' to confirm"
        if ($confirmation -ne "yes") {
            Write-Status "Reset cancelled" "Warning"
            exit 0
        }

        Write-Host "Destroying container and volume..."
        docker-compose down -v postgres 2>&1 | Out-Null

        Write-Host "Recreating container..."
        docker-compose up -d postgres

        if (Wait-ForPostgres) {
            Write-Status "PostgreSQL reset complete" "Success"
            Write-Host ""
            Write-Host "Next steps:"
            Write-Host "  1. Run migrations: python migrate_db.py"
            Write-Host "  2. Import data: python scripts/import_all_data.py --source <backup.json>"
        } else {
            Write-Status "PostgreSQL failed to start after reset" "Error"
            exit 1
        }
    }

    "logs" {
        Write-Status "Showing PostgreSQL logs (Ctrl+C to exit)..."
        docker-compose logs -f postgres
    }

    "shell" {
        Write-Status "Opening PostgreSQL shell..."
        docker exec -it $ContainerName psql -U omnitool -d omnitool_dev
    }

    "status" {
        $running = docker ps --filter "name=$ContainerName" --format "{{.Names}}" 2>&1
        if ($running -eq $ContainerName) {
            Write-Status "PostgreSQL is running" "Success"

            # Show container details
            docker ps --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

            # Check health
            $health = docker inspect --format='{{.State.Health.Status}}' $ContainerName 2>&1
            Write-Host ""
            Write-Host "Health: $health"
        } else {
            Write-Status "PostgreSQL is not running" "Warning"
            Write-Host "Start with: .\scripts\docker-db.ps1 start"
        }
    }
}
