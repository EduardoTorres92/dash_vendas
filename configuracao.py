"""
Configuração em uso: os valores de `config_negocio.py` (exemplo genérico),
sobrepostos pelos de `config_local.py` quando esse arquivo existe.

O `config_local.py` fica só no computador onde o painel roda com dados reais
(está no .gitignore). Veja as instruções em `config_negocio.py`.
"""

from config_negocio import *  # noqa: F401,F403

try:
    from config_local import *  # noqa: F401,F403

    ORIGEM = "config_local.py"
except ModuleNotFoundError:
    ORIGEM = "config_negocio.py (exemplo)"
