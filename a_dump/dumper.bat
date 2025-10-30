@echo off
chcp 65001 >nul
title Execução Sequencial do Dumper Aulete

echo ============================================
echo      EXECUÇÃO SEQUENCIAL DOS 5 MÓDULOS
echo ============================================
echo.

setlocal enabledelayedexpansion

rem Caminho da pasta onde estão os scripts
set "DUMPER_DIR=%~dp0dumper"

if not exist "%DUMPER_DIR%" (
    echo ERRO: A pasta "dumper" nao foi encontrada no mesmo diretorio deste arquivo.
    pause
    exit /b
)

rem ======== ETAPA 1 ========
echo [1/5] Executando getsitemap.py ...
python "%DUMPER_DIR%\[1] getsitemap.py"
if errorlevel 1 (
    echo ERRO ao executar getsitemap.py
    pause
    exit /b
)

rem ======== ETAPA 2 ========
echo.
echo [2/5] Executando gethtml.py ...
python "%DUMPER_DIR%\[2] gethtml.py"
if errorlevel 1 (
    echo ERRO ao executar gethtml.py
    pause
    exit /b
)

rem ======== ETAPA 3 ========
echo.
echo [3/5] Executando txtconvert.py ...
python "%DUMPER_DIR%\[3] txtconvert.py"
if errorlevel 1 (
    echo ERRO ao executar txtconvert.py
    pause
    exit /b
)

rem ======== ETAPA 4 ========
echo.
echo [4/5] Executando junkdatacleaner.py ...
python "%DUMPER_DIR%\[4] junkdatacleaner.py"
if errorlevel 1 (
    echo ERRO ao executar junkdatacleaner.py
    pause
    exit /b
)

rem ======== ETAPA 5 ========
echo.
echo [5/5] Executando uselessdatacleaner.py ...
python "%DUMPER_DIR%\[5] uselessdatacleaner.py"
if errorlevel 1 (
    echo ERRO ao executar uselessdatacleaner.py
    pause
    exit /b
)

echo.
echo ============================================
echo TODOS OS PROCESSOS FORAM EXECUTADOS COM SUCESSO!
echo ============================================
pause
