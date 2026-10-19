#!/bin/bash
cd "$(dirname "$0")"
mkdir -p logs
venv/bin/python collect.py >> logs/collect.log 2>&1
