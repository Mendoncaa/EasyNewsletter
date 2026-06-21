@echo off
REM EasyNewsletter - Daily Digest Generator
REM Schedule this script via Windows Task Scheduler

cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py --days 1
