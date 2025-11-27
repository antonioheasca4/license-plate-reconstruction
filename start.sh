#!/bin/bash
# Start Script - License Plate Reconstruction System
# Starts Frontend + Backend + PostgreSQL

echo -e "\033[36mStarting License Plate Reconstruction System...\033[0m"
echo -e "\033[37m   (Frontend + Backend + PostgreSQL)\033[0m"
echo ""

# Check Docker
echo -e "\033[33mChecking Docker...\033[0m"
if ! docker info > /dev/null 2>&1; then
    echo -e "\033[31mDocker is not running!\033[0m"
    echo -e "\033[33mPlease start Docker and try again.\033[0m"
    exit 1
fi
echo -e "\033[32mDocker is running\033[0m"

# Start PostgreSQL
echo ""
echo -e "\033[33mStarting PostgreSQL...\033[0m"
containerStatus=$(docker ps -a --filter "name=lpr_postgres" --format "{{.Status}}" 2>/dev/null)
if [[ $containerStatus == *"Up"* ]]; then
    echo -e "\033[32mPostgreSQL already running\033[0m"
else
    # Start only PostgreSQL service (not all services)
    docker-compose up -d postgres
    echo -e "\033[32mPostgreSQL started\033[0m"
fi

# Wait for PostgreSQL
echo ""
echo -e "\033[33mWaiting for PostgreSQL...\033[0m"
maxAttempts=30
attempt=0
while [ $attempt -lt $maxAttempts ]; do
    attempt=$((attempt + 1))
    pgReady=$(docker exec lpr_postgres pg_isready -U lpr_user -d lpr_database 2>/dev/null)
    if [[ $pgReady == *"accepting connections"* ]]; then
        echo -e "\033[32mPostgreSQL ready!\033[0m"
        break
    fi
    sleep 1
done

# Start Frontend in background
echo ""
echo -e "\033[36mStarting React Frontend...\033[0m"

if [ ! -d "frontend/node_modules" ]; then
    echo -e "\033[33mInstalling frontend dependencies (first time)...\033[0m"
    cd frontend
    npm install
    cd ..
fi

cd frontend
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "\033[32mFrontend started in background (PID: $FRONTEND_PID)\033[0m"
sleep 2

# Start Backend in foreground
echo ""
echo -e "\033[36mStarting FastAPI Backend...\033[0m"
echo -e "\033[36m-------------------------------------------------------\033[0m"
echo ""
echo -e "\033[37mURLs:\033[0m"
echo -e "\033[36m   Frontend:  http://localhost:3000\033[0m"
echo -e "\033[36m   Backend:   http://localhost:8000\033[0m"
echo -e "\033[36m   API Docs:  http://localhost:8000/docs\033[0m"
echo ""
echo -e "\033[90mPress Ctrl+C to stop everything...\033[0m"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "\033[33mShutting down...\033[0m"
    
    echo -e "\033[33mStopping frontend...\033[0m"
    kill $FRONTEND_PID 2>/dev/null
    
    # Kill all node processes related to this project
    pkill -f "vite" 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    
    echo -e "\033[32mAll services stopped\033[0m"
    echo ""
    echo -e "\033[90mTip: PostgreSQL is still running in Docker\033[0m"
    echo -e "\033[90m   Use './stop.sh' to stop Docker too\033[0m"
    
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

cd backend

# Activate virtual environment and start backend
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python main.py
else
    echo -e "\033[33mVirtual environment not found. Creating...\033[0m"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate it
    source venv/bin/activate
    
    # Install dependencies
    echo -e "\033[33mInstalling dependencies...\033[0m"
    pip install -r requirements.txt
    
    # Start backend
    echo -e "\033[32mSetup complete! Starting backend...\033[0m"
    python main.py
fi
