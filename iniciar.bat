@echo off
setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 -m src.main %*
) else (
    python -m src.main %*
)
if errorlevel 1 (
    echo.
    echo Verifique se o Python 3.10 ou superior esta instalado.
    echo Consulte o arquivo COMECAR_AQUI.pdf.
)
pause
