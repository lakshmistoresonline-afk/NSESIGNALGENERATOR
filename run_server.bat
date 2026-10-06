@echo off
setlocal
cd /d "%~dp0"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
set PYTHONPATH=%CD%\src
python -m uvicorn server.api:app --host 0.0.0.0 --port 8010
