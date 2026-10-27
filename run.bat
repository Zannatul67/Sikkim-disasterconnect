@echo off
cd /d "%~dp0backend"
pip install -r requirements.txt
python app.py
pause
