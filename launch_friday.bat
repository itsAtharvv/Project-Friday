@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%"

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found on PATH.
    popd
    exit /b 1
)

python main.py
set "EXIT_CODE=%ERRORLEVEL%"

popd
exit /b %EXIT_CODE%