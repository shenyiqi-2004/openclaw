@echo off
setlocal
pushd "%~dp0" >nul 2>&1
if errorlevel 1 (
  echo Failed to enter script directory: %~dp0
  exit /b 1
)
echo ============================================
echo mouse_bridge.py - TCP Mouse Control Server
echo ============================================
echo.
echo Working dir: %CD%
echo IMPORTANT: Keep this window open while using!
echo Press Ctrl+C to stop.
echo.
py -3 mouse_bridge.py
set "EXIT_CODE=%ERRORLEVEL%"
popd
pause
exit /b %EXIT_CODE%
