@echo off
color 1f

cls
echo ============================
echo       BUSCA DE VERBETES
echo ============================

python -u ./search/search.py

echo Saindo...
color 07
exit /b
