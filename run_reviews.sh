#!/bin/bash
cd "$(dirname "$0")"
mkdir -p logs
venv/bin/python collect_reviews.py "$@" >> logs/reviews.log 2>&1
