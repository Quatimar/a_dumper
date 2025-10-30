@echo off
color 1f
chcp 65001
setlocal enabledelayedexpansion

:: Caminho da pasta de busca
set "BASE_DIR=%~dp0auletetxt"

:MENU
cls
echo ============================
echo       BUSCA DE VERBETES
echo ============================
echo.
set /p "TERM=Digite a palavra para buscar (ou ENTER para sair): "

if "%TERM%"=="" goto END

:: Limpa variáveis
set "COUNT=0"
set "FILES="

:: Procurar arquivos
for /r "%BASE_DIR%" %%F in (*.txt) do (
    set "FNAME=%%~nF"
    echo !FNAME! | findstr /i "\<%TERM%\>" >nul
    if not errorlevel 1 (
        set /a COUNT+=1
        set "FILES[!COUNT!]=%%F"
        echo [!COUNT!] !FNAME!
    )
)

:: Se nenhum arquivo encontrado
if "%COUNT%"=="0" (
    echo.
    echo Nenhum arquivo encontrado contendo "%TERM%".
    pause
    goto MENU
)

:: Adiciona opção de cancelar
set /a COUNT+=1
set "FILES[!COUNT!]=CANCEL"
echo [!COUNT!] Cancelar busca

:: Seleção do usuário
:SELECIONA
echo.
set /p "OP=Escolha uma opcao: "
if not defined FILES[%OP%] (
    echo Opcao invalida!
    goto SELECIONA
)

if "!FILES[%OP%]!"=="CANCEL" goto MENU

:: Exibe conteúdo do arquivo selecionado
type "!FILES[%OP%]!"
echo.
pause
goto MENU

:END
echo Saindo...
exit /b
