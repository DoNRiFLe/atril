@echo off
setlocal
rem Igual que alinear.bat, pero primero aisla la voz con demucs.
rem Usalo para los temas donde la banda tapa la voz.
rem Tarda varios minutos por tema; la voz aislada queda cacheada al lado
rem del audio como <nombre>.vocals.wav, asi el segundo intento es rapido.

if "%~1"=="" (
  echo Arrastra el archivo de audio sobre este .bat
  pause & exit /b 1
)

set "PY=%~dp0..\.venv-alineador\Scripts\python.exe"
if not exist "%PY%" (
  echo Falta el entorno. Corre primero:
  echo   powershell -ExecutionPolicy Bypass -File "%~dp0instalar-alineador.ps1"
  pause & exit /b 1
)

"%PY%" -c "import demucs" 2>nul
if errorlevel 1 (
  echo Falta demucs. Instalalo con:
  echo   "%PY%" -m pip install demucs
  echo Ojo: se trae PyTorch, unos 2,5 GB.
  pause & exit /b 1
)

set "LETRA=%~2"
if "%LETRA%"=="" set "LETRA=%~dpn1.txt"
if not exist "%LETRA%" (
  echo No encontre la letra: %LETRA%
  pause & exit /b 1
)

echo Aislando la voz y alineando "%~nx1" ... (varios minutos)
"%PY%" "%~dp0alinear.py" "%~1" "%LETRA%" -o "%~dpn1.lrc" -m small --separar
echo.
echo Importa el .lrc desde el Atril: menu Temas - Importar
pause
