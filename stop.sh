#!/bin/bash
# Stop Script for License Plate Reconstruction
# Stops Backend + Docker PostgreSQL (optional)

KEEP_DOCKER=false
REMOVE_DATA=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-docker)
            KEEP_DOCKER=true
            shift
            ;;
        --remove-data)
            REMOVE_DATA=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./stop.sh [--keep-docker] [--remove-data]"
            exit 1
            ;;
    esac
done

echo -e "\033[36mStopping License Plate Reconstruction System...\033[0m"
echo ""

# Stop Python processes (backend)
echo -e "\033[33mStopping backend processes...\033[0m"
pythonProcesses=$(pgrep -f "python.*main.py" 2>/dev/null)
if [ -n "$pythonProcesses" ]; then
    pkill -f "python.*main.py"
    echo -e "\033[32mBackend stopped\033[0m"
else
    echo -e "\033[90mNo backend processes running\033[0m"
fi

# Stop Node processes (frontend)
echo ""
echo -e "\033[33mStopping frontend processes...\033[0m"
nodeProcesses=$(pgrep -f "vite|npm run dev" 2>/dev/null)
if [ -n "$nodeProcesses" ]; then
    pkill -f "vite"
    pkill -f "npm run dev"
    echo -e "\033[32mFrontend stopped\033[0m"
else
    echo -e "\033[90mNo frontend processes running\033[0m"
fi

# Stop Docker (unless --keep-docker is specified)
if [ "$KEEP_DOCKER" = false ]; then
    echo ""
    echo -e "\033[33mStopping PostgreSQL container...\033[0m"
    
    if [ "$REMOVE_DATA" = true ]; then
        echo -e "\033[31mWARNING: Removing container AND data!\033[0m"
        docker-compose down -v
        echo -e "\033[32mPostgreSQL stopped and data removed\033[0m"
    else
        docker-compose down
        echo -e "\033[32mPostgreSQL stopped (data preserved)\033[0m"
    fi
else
    echo ""
    echo -e "\033[90mKeeping PostgreSQL container running\033[0m"
fi

echo ""
echo -e "\033[32mSystem stopped successfully\033[0m"
echo ""
echo -e "\033[90mUsage examples:\033[0m"
echo -e "\033[90m   ./stop.sh                  - Stop all services\033[0m"
echo -e "\033[90m   ./stop.sh --keep-docker    - Stop only app, keep PostgreSQL\033[0m"
echo -e "\033[90m   ./stop.sh --remove-data    - Stop all and remove database data\033[0m"
