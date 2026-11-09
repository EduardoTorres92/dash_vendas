@echo off
REM Abre o painel de faturamento neste computador (Windows).
REM Na primeira vez cria o ambiente Python e instala as dependencias.
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente Python na pasta .venv ...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if errorlevel 1 (
        echo.
        echo Nao foi possivel criar o ambiente. Instale o Python 3.10 ou mais novo
        echo ^(https://www.python.org/downloads/^) e marque "Add python.exe to PATH".
        pause
        exit /b 1
    )
)

echo Conferindo dependencias...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo.
    echo Falha ao instalar as dependencias. Se a rede da empresa usa proxy,
    echo configure-o no pip ^(pip config set global.proxy http://usuario:senha@proxy:porta^).
    pause
    exit /b 1
)

echo Abrindo o painel em http://localhost:8501 ... ^(feche esta janela para encerrar^)
".venv\Scripts\python.exe" -m streamlit run faturamento.py
pause
