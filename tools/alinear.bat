@echo off
setlocal
rem Arrastra un archivo de audio sobre este .bat.
rem Busca al lado un .txt con la letra y el mismo nombre, y escribe el .lrc.

if "%~1"=="" (
  echo Arrastra el archivo de audio sobre este .bat
  echo   o usa:  alinear.bat tema.mp3 [letra.txt]
  pause & exit /b 1
)

set "RAIZ=%~dp0.."
set "PY=%RAIZ%\.venv-alineador\Scripts\python.exe"
if not exist "%PY%" (
  echo Falta el entorno. Corre primero:
  echo   powershell -ExecutionPolicy Bypass -File "%~dp0instalar-alineador.ps1"
  pause & exit /b 1
)

set "AUDIO=%~1"
set "LETRA=%~2"
if "%LETRA%"=="" set "LETRA=%~dpn1.txt"
if not exist "%LETRA%" (
  echo No encontre la letra: %LETRA%
  echo Guarda la letra en un .txt con el mismo nombre que el audio.
  pause & exit /b 1
)

echo Alineando "%~nx1" ...
"%PY%" "%~dp0alinear.py" "%AUDIO%" "%LETRA%" -o "%~dpn1.lrc" -m small
echo.
echo Importa el .lrc desde el Atril: menu Temas - Importar
pause
