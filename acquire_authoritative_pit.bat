@echo off
setlocal
python scripts\acquire_authoritative_pit.py --start %1 --end %2
if errorlevel 1 exit /b %errorlevel%
echo Official NSE PIT acquisition completed.
