@echo off
if "%~1"=="onboard" (
    python scripts\onboard.py
) else (
    echo.
    echo 🚀 AI-Aero CLI
    echo.
    echo Usage:
    echo   aero onboard    - Launch the agent configuration tool
    echo.
)
