@echo off
setlocal enabledelayedexpansion

echo.
echo ================================================================
echo              YawStar Proxy Hunter - Windows Setup
echo ================================================================
echo                    Designed by: YawHackka
echo ================================================================
echo.

echo [ERROR] Native Windows installation is not supported!
echo.
echo This project requires a Unix-like environment to run properly.
echo.
echo Please use one of these options:
echo.
echo   1. WSL2 (Recommended)
echo      - Open PowerShell as Administrator
echo      - Run: wsl --install
echo      - Restart your computer
echo      - Open Ubuntu from Start Menu
echo      - Run: bash install.sh
echo.
echo   2. Git Bash
echo      - Install Git for Windows: https://git-scm.com/download/win
echo      - Open Git Bash
echo      - Run: bash install.sh
echo.
echo   3. Docker (Advanced)
echo      - Install Docker Desktop
echo      - Run the project in a Linux container
echo.
echo For detailed instructions visit:
echo https://github.com/YawStar/Proxy-Hunter
echo.

pause
exit /b 1
