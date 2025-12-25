@echo off
set PYTHONPATH=%PYTHONPATH%;%CD%\src
python web/server.py
pause
