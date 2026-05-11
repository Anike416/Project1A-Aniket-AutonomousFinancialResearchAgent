@echo off
REM Windows batch script to run ARA-1 Streamlit Dashboard

echo.
echo ==============================================
echo.    ARA-1 Streamlit Dashboard Launcher
echo.
echo ==============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "myenv" (
    echo WARNING: Virtual environment 'myenv' not found
    echo Please run: python -m venv myenv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call myenv\Scripts\activate.bat

REM Install/update dependencies
echo.
echo Checking dependencies...
pip install -q -r requirements.txt

REM Run Streamlit
echo.
echo Starting ARA-1 Dashboard...
echo Dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py --theme.primaryColor="#0D47A1" --theme.backgroundColor="#F5F5F5" --theme.secondaryBackgroundColor="#FFFFFF" --theme.textColor="#262730" --theme.font="sans serif"

pause
