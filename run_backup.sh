#!/bin/bash
cd "$(dirname "$0")"
mkdir -p logs
venv/bin/python backup.py >> logs/backup.log 2>&1
