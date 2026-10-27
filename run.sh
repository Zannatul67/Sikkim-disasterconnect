#!/bin/sh
cd "$(dirname "$0")/backend" && pip install -r requirements.txt && python3 app.py
