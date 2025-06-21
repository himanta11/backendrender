#!/usr/bin/env bash
# Start script for Render deployment

echo "Starting Aspirant Backend..."

# Set environment variables if not already set
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}

# Run database migrations (if needed)
echo "Checking database connection..."
python -c "
import sys
sys.path.append('backend')
from database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
"

# Start the FastAPI application
echo "Starting FastAPI application on $HOST:$PORT..."
exec uvicorn backend.main:app --host $HOST --port $PORT --workers 1 