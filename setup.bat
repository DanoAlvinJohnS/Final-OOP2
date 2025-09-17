@echo off
echo ================================================================
echo Setting up Python Virtual Environment | By: Dano Alvin John 
echo ================================================================

REM Create venv
python -m venv venv

REM Activate venv
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

echo ================================================================
echo Setup Complete!
echo To activate your environment later, run:
echo     venv\Scripts\activate
echo ================================================================
pause
