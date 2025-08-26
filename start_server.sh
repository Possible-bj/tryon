#!/bin/bash

# Activate the virtual environment
source /root/ds_tjc/venv/bin/activate

# Kill any process running on port 5302
PORT=5302
echo "Checking for processes on port $PORT..."
if pid=$(lsof -ti:$PORT); then
    echo "Killing process(es) on port $PORT..."
    kill -9 $pid
    sleep 2
fi

# Clean up old PID file if it exists
if [ -f uvicorn.pid ]; then
    rm -f uvicorn.pid
fi

# Set PYTHONPATH
export PYTHONPATH="/root/ds_tjc/src"
# nohup uvicorn main:app --host 0.0.0.0 --port 5302 --reload --log-level info --timeout-keep-alive 300 >> uvicorn.log 2>&1 &
# Start Uvicorn with timeout of 300 seconds
nohup uvicorn marketing_assistant_ai.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --reload \
    --log-level info \
    --timeout-keep-alive 300 \
    >> uvicorn.log 2>&1 &

# Store the new PID
echo $! > uvicorn.pid
echo "Uvicorn started with PID $(cat uvicorn.pid)"