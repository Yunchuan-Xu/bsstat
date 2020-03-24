#!/usr/bin/env bash
nohup gunicorn -b 0.0.0.0:5000 algoweb:app --log-level=info --access-logfile=access.log --error-logfile=error.log 2>&1 &
nohup python -u bs.py > out 2>&1 &
