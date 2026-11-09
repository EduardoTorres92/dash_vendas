#!/usr/bin/env bash
# Abre o painel de faturamento neste computador (macOS/Linux).
# Na primeira vez cria o ambiente Python e instala as dependências.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "Criando ambiente Python na pasta .venv ..."
    python3 -m venv .venv || {
        echo "Não foi possível criar o ambiente. Instale o Python 3.10 ou mais novo."
        exit 1
    }
fi

echo "Conferindo dependências..."
.venv/bin/python -m pip install --disable-pip-version-check -q -r requirements.txt

echo "Abrindo o painel em http://localhost:8501 ... (Ctrl+C para encerrar)"
exec .venv/bin/python -m streamlit run faturamento.py
