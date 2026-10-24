#!/bin/bash
cd "$(dirname "$0")"
mkdir -p logs
set -a; [ -f .env ] && source .env; set +a
venv/bin/python health_check.py >> logs/health.log 2>&1
