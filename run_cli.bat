@echo off
set PYTHONPATH=%PYTHONPATH%;%CD%\src
python game.py %*
pause
