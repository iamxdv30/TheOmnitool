#!/bin/bash
#
# Docker PostgreSQL management script for Linux/Mac
#
# Usage:
#   ./scripts/docker-db.sh start   - Start PostgreSQL container
#   ./scripts/docker-db.sh stop    - Stop container (preserve data)
#   ./scripts/docker-db.sh reset   - Destroy all data and recreate
#   ./scripts/docker-db.sh logs    - View container logs
#   ./scripts/docker-db.sh shell   - Open PostgreSQL shell
#   ./scripts/docker-db.sh status  - Check container status

set -e

CONTAINER_NAME="omnitool-postgres"
MAX_RETRIES=30
RETRY_INTERVAL=1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    local type=$1
    local message=$2
    case $type in
        success) echo -e "${GREEN}[OK]${NC} $message" ;;
        error)   echo -e "${RED}[ERROR]${NC} $message" ;;
        warning) echo -e "${YELLOW}[WARN]${NC} $message" ;;
        *)       echo -e "${CYAN}[INFO]${NC} $message" ;;
    esac
}

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_status error "Docker is not running. Please start Docker."
        exit 1
    fi
}

wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..."
    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if docker exec $CONTAINER_NAME pg_isready -U omnitool -d omnitool_dev > /dev/null 2>&1; then
            return 0
        fi
        retries=$((retries + 1))
        echo "  Attempt $retries/$MAX_RETRIES..."
        sleep $RETRY_INTERVAL
    done
    return 1
}

# Check Docker is available
check_docker

case "$1" in
    start)
        print_status info "Starting PostgreSQL container..."

        # Check if already running
        if docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
            print_status warning "PostgreSQL is already running"
            exit 0
        fi

        # Start container
        docker-compose up -d postgres

        if wait_for_postgres; then
            print_status success "PostgreSQL is ready on localhost:5432"
            echo ""
            echo "Connection Details:"
            echo "  Host:     localhost"
            echo "  Port:     5432"
            echo "  Database: omnitool_dev"
            echo "  User:     omnitool"
            echo "  Password: omnitool_dev"
            echo ""
            echo "Connection URL:"
            echo "  postgresql://omnitool:omnitool_dev@localhost:5432/omnitool_dev"
        else
            print_status error "PostgreSQL failed to start within timeout"
            echo "Check logs with: ./scripts/docker-db.sh logs"
            exit 1
        fi
        ;;

    stop)
        print_status info "Stopping PostgreSQL container..."
        docker-compose stop postgres
        print_status success "PostgreSQL stopped (data preserved)"
        ;;

    reset)
        print_status warning "Resetting PostgreSQL (ALL DATA WILL BE LOST)..."

        read -p "Are you sure? Type 'yes' to confirm: " confirmation
        if [ "$confirmation" != "yes" ]; then
            print_status warning "Reset cancelled"
            exit 0
        fi

        echo "Destroying container and volume..."
        docker-compose down -v postgres 2>/dev/null || true

        echo "Recreating container..."
        docker-compose up -d postgres

        if wait_for_postgres; then
            print_status success "PostgreSQL reset complete"
            echo ""
            echo "Next steps:"
            echo "  1. Run migrations: python migrate_db.py"
            echo "  2. Import data: python scripts/import_all_data.py --source <backup.json>"
        else
            print_status error "PostgreSQL failed to start after reset"
            exit 1
        fi
        ;;

    logs)
        print_status info "Showing PostgreSQL logs (Ctrl+C to exit)..."
        docker-compose logs -f postgres
        ;;

    shell)
        print_status info "Opening PostgreSQL shell..."
        docker exec -it $CONTAINER_NAME psql -U omnitool -d omnitool_dev
        ;;

    status)
        if docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
            print_status success "PostgreSQL is running"
            docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            echo ""
            health=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null || echo "unknown")
            echo "Health: $health"
        else
            print_status warning "PostgreSQL is not running"
            echo "Start with: ./scripts/docker-db.sh start"
        fi
        ;;

    *)
        echo "Usage: $0 {start|stop|reset|logs|shell|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start PostgreSQL container"
        echo "  stop    - Stop container (preserves data)"
        echo "  reset   - Destroy all data and recreate container"
        echo "  logs    - View container logs (follow mode)"
        echo "  shell   - Open PostgreSQL interactive shell"
        echo "  status  - Check if container is running"
        exit 1
        ;;
esac
