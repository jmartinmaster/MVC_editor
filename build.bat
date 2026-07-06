@echo off
echo Installing requirements...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install requirements. Please ensure pip is installed and in your PATH.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Building executable with PyInstaller...
pyinstaller --onefile --noconsole --name "MVC_Editor" main.py
if %ERRORLEVEL% neq 0 (
    echo Failed to compile executable. Please verify PyInstaller is installed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Build completed successfully. Check the 'dist' directory for MVC_Editor.exe!
pause
