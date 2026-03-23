#!/usr/bin/env bash
# Start backend and frontend dev servers concurrently.
# Usage: ./run/dev.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cleanup() { kill 0 2>/dev/null; }
trap cleanup EXIT

echo "Starting backend on :8000 ..."
cd "$ROOT" && uv run uvicorn mindspace.web.app:create_app --factory --port 8000 --reload &

echo "Starting frontend on :5173 ..."
cd "$ROOT/frontend" && npm run dev &

wait
