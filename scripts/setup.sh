#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Setting up backend environment..."
cd "$ROOT_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

echo "Setting up frontend environment..."
cd "$ROOT_DIR/frontend"
npm install

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

echo "Setup complete."
echo
echo "Next steps:"
echo "  1. Make sure PostgreSQL is running and reachable via DATABASE_URL."
echo "  2. From backend/, activate the venv and apply migrations:"
echo "       source .venv/bin/activate && alembic upgrade head"
echo "     If you already have a pre-Alembic Phase 2 database, run this once instead:"
echo "       alembic stamp 0001_baseline_phase_2"
echo "  3. Start the backend: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "  4. Start the frontend: (from frontend/) npm run dev -- --host 0.0.0.0 --port 5173"
