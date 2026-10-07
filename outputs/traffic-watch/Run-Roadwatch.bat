@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0serve.py" (
  echo Roadwatch cannot start from inside the ZIP preview.
  echo Extract the ZIP first, then run this file from the extracted traffic-watch folder.
  pause
  exit /b 1
)
where py >nul 2>nul
if not errorlevel 1 (
  echo Starting Roadwatch with Python...
  py -3 serve.py
  if not errorlevel 1 goto :end
  echo Python launcher could not keep the Roadwatch server running.
)
set "CODEXPY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%CODEXPY%" (
  echo Trying the bundled Python runtime...
  "%CODEXPY%" serve.py
  if not errorlevel 1 goto :end
  echo Roadwatch stopped or could not start. Read the error above.
  pause
  goto :eof
)
echo.
echo Roadwatch needs Python 3. Install it from python.org, then run this file again.
pause
:end
echo Roadwatch server stopped.
pause
