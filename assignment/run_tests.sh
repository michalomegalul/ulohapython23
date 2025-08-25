#!/bin/bash
set -euo pipefail

echo "====================================="
echo "         Test Runner"
echo "====================================="

echo "[1/5] Stopping existing containers..."
#docker-compose down -v || echo "No containers to stop."

echo "[2/5] Starting services..."
docker-compose up -d

echo "[3/5] Waiting for database to be ready..."
until docker-compose exec -T db pg_isready -U user -d domains > /dev/null 2>&1; do
  echo "  Waiting for DB..."
  sleep 2
done
echo "  Database is ready."

echo "[4/5] Initializing test data..."
docker-compose exec -T app python -m cli.init_db || {
  echo "Failed to initialize DB"
  exit 1
}

echo "[5/5] Running tests..."
docker-compose exec -T app python -m pytest tests/ -v || {
  echo "Tests failed!"
  exit 1
}

echo "Final status check..."
docker-compose exec -T app python cli.py status

echo "====================================="
echo "All tests completed successfully!"
echo "====================================="
