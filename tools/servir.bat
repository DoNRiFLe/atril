@echo off
rem Doble clic para levantar el Atril en http://localhost:3000/letras.html
cd /d "%~dp0.."
node tools\servir.js %*
pause
