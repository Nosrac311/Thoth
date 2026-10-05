@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ========================================
echo Starting Thoth...
echo ========================================
echo.

set "THOTH_DIR=%~dp0"
set "VENV_DIR=%THOTH_DIR%.venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "REQUIREMENTS=%THOTH_DIR%requirements.txt"

REM ========================================
REM Find a working system Python
REM ========================================

echo Checking system Python...

set "SYSTEM_PYTHON="

REM Try Python Launcher first
where py >nul 2>&1
if %errorlevel%==0 (
    py -3.13 --version >nul 2>&1
    if %errorlevel%==0 (
        set "SYSTEM_PYTHON=py -3.13"
        goto :system_python_found
    )

    py --version >nul 2>&1
    if %errorlevel%==0 (
        set "SYSTEM_PYTHON=py"
        goto :system_python_found
    )
)

REM Try regular Python command
where python >nul 2>&1
if %errorlevel%==0 (
    python --version >nul 2>&1
    if %errorlevel%==0 (
        set "SYSTEM_PYTHON=python"
        goto :system_python_found
    )
)

echo.
echo ERROR: No working Python installation was found.
echo.
echo Install Python 3.13 on this computer and try again.
echo.
pause
exit /b 1

:system_python_found

echo System Python found:
%SYSTEM_PYTHON% --version
echo.

REM ========================================
REM Test existing virtual environment
REM ========================================

if exist "%PYTHON%" (
    echo Testing existing Thoth virtual environment...

    "%PYTHON%" --version >nul 2>&1

    if %errorlevel%==0 (
        echo Existing virtual environment is working.
        goto :venv_ready
    )

    echo.
    echo Existing virtual environment is BROKEN.
    echo It points to a Python installation that no longer exists.
    echo.
    echo Removing broken virtual environment...

    rmdir /s /q "%VENV_DIR%"

    if exist "%VENV_DIR%" (
        echo.
        echo ERROR: Could not remove the broken .venv folder.
        echo Close any programs using Thoth and try again.
        echo.
        pause
        exit /b 1
    )

    echo Broken virtual environment removed.
    echo.
)

REM ========================================
REM Create fresh virtual environment
REM ========================================

echo Creating a new Thoth virtual environment...
echo.

%SYSTEM_PYTHON% -m venv "%VENV_DIR%"

if not exist "%PYTHON%" (
    echo.
    echo ERROR: Failed to create the virtual environment.
    echo.
    pause
    exit /b 1
)

echo.
echo Virtual environment created successfully.
echo.

:venv_ready

REM ========================================
REM Verify virtual environment
REM ========================================

echo Verifying Thoth Python...

"%PYTHON%" --version

if %errorlevel% neq 0 (
    echo.
    echo ERROR: The Thoth virtual environment is not working.
    echo.
    pause
    exit /b 1
)

echo.
echo Python executable:
"%PYTHON%" -c "import sys; print(sys.executable)"
echo.

REM ========================================
REM Upgrade pip
REM ========================================

echo Updating pip...
echo.

"%PYTHON%" -m pip install --upgrade pip

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Could not update pip.
    echo.
    pause
    exit /b 1
)

echo.
echo Pip is ready.
echo.

REM ========================================
REM Install dependencies
REM ========================================

if exist "%REQUIREMENTS%" (

    echo Installing/checking Python dependencies...
    echo.

    "%PYTHON%" -m pip install -r "%REQUIREMENTS%"

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install Python dependencies.
        echo.
        pause
        exit /b 1
    )

    echo.
    echo Dependencies installed successfully.
    echo.

) else (

    echo WARNING: requirements.txt was not found.
    echo.
    echo Installing required dependency: python-dotenv
    echo.

    "%PYTHON%" -m pip install python-dotenv

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install python-dotenv.
        echo.
        pause
        exit /b 1
    )

    echo.
    echo python-dotenv installed.
    echo.
)

REM ========================================
REM Verify python-dotenv
REM ========================================

echo Verifying python-dotenv...

"%PYTHON%" -c "from dotenv import load_dotenv; print('python-dotenv: OK')"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: python-dotenv is not installed correctly.
    echo.
    echo Installing it now...
    echo.

    "%PYTHON%" -m pip install --upgrade python-dotenv

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Could not install python-dotenv.
        echo.
        pause
        exit /b 1
    )

    "%PYTHON%" -c "from dotenv import load_dotenv; print('python-dotenv: OK')"

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: python-dotenv still cannot be imported.
        echo.
        pause
        exit /b 1
    )
)

echo.

REM ========================================
REM Load GitHub token
REM ========================================

if not exist "%THOTH_DIR%github_token.txt" (
    echo ERROR: github_token.txt was not found.
    echo.
    echo Create github_token.txt in the Thoth folder
    echo and put your GitHub token inside it.
    echo.
    pause
    exit /b 1
)

set /p GITHUB_TOKEN=<"%THOTH_DIR%github_token.txt"

if "%GITHUB_TOKEN%"=="" (
    echo ERROR: GitHub token is empty.
    echo.
    pause
    exit /b 1
)

echo GitHub token loaded.
echo.

REM ========================================
REM Start Thoth
REM ========================================

if not exist "%THOTH_DIR%run_launcher.py" (
    echo ERROR: run_launcher.py was not found.
    echo.
    pause
    exit /b 1
)

echo ========================================
echo Starting Thoth with:
echo %PYTHON%
echo ========================================
echo.

"%PYTHON%" "%THOTH_DIR%run_launcher.py"

echo.
echo ========================================
echo Thoth has exited.
echo ========================================
pause

endlocal
