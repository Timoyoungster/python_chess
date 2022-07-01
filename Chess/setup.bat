@echo off

:: Check for Python Installation
python --version 3>NUL
if errorlevel 1 goto errorNoPython

:: Reaching here means Python is installed.
:: Execute stuff...
python3 -m pip3 install -r requirements.txt

:: Once done, exit the batch file -- skips executing the errorNoPython section
goto:eof

:errorNoPython
echo.
echo Error^: Python not installed
set /p ans="Do you want to install it? [y/n]"
if %ans% == "y" python