@echo off
REM IoTShield AI - one-click launcher for Windows (safe simulation only)
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher "py" not found. Install Python 3.10+ from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  pause
  exit /b 1
)
if not exist .venv (
  echo Creating virtual environment...
  py -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install -q -r requirements.txt
if not exist models\ransomware_rf.joblib (
  echo Training the detection model on synthetic data...
  python train_model.py
)
echo Starting IoTShield AI dashboard - your browser will open automatically.
python -m streamlit run app.py
pause