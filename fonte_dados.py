"""
Fonte de dados do dashboard: arquivos enviados pela tela ou demonstração.

Uso local: o relatório de faturamento (ESFT0100, .csv) e, opcionalmente, a
planilha de embarques (.xlsx) são enviados pela tela inicial. Os arquivos
ficam só na memória do processo do Streamlit, neste computador: nada é
gravado em disco nem enviado para fora, e ao fechar o app é preciso
carregá-los de novo.

Sem arquivos, o modo demonstração usa os dados fictícios do repositório
(ESFT0100_processado.csv e embarques_falsos.xlsx).
"""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd
import streamlit as st

import ui_theme as ui

CHAVE_SESSAO = "fonte_dados"
TAMANHO_MINIMO_COLUNAS = 3  # menos que isso quase sempre é separador errado


class ArquivoInvalido(Exception):
    """Arquivo enviado não está no formato esperado (mensagem para o usuário)."""


class SemEmbarques(Exception):
    """Dados reais carregados sem a planilha de embarques (seção de potencial fica indisponível)."""


@dataclass(frozen=True)
class FonteDados:
    tipo: str  # "arquivo" | "demo"
    nome: str = ""
    csv: Optional[bytes] = None
    embarques: Optional[bytes] = None
    embarques_nome: str = ""
    chave: str = "demo"  # identifica o conteúdo, para o cache do Streamlit

    @property
    def demonstracao(self) -> bool:
        return self.tipo == "demo"

    @property
    def anonimizar(self) -> bool:
        # Dados reais, no computador da empresa, aparecem como estão.
        return self.demonstracao

    @property
    def tem_embarques(self) -> bool:
        return self.demonstracao or self.embarques is not None

    def arquivo_embarques(self):
        """Planilha de embarques para o ETL (None = arquivo de demonstração)."""
        return io.BytesIO(self.embarques) if self.embarques is not None else None


def _hash(*partes: Optional[bytes]) -> str:
    h = hashlib.sha256()
    for parte in partes:
        h.update(parte or b"")
        h.update(b"\0")
    return h.hexdigest()[:16]


def ler_esft0100(conteudo: bytes, colunas: Iterable[str]) -> pd.DataFrame:
    """
    Lê o relatório ESFT0100 no formato original do ERP (CSV separado por ";",
    codificação latin1) e devolve só as colunas usadas pelo dashboard.
    """
    colunas = list(dict.fromkeys(colunas))
    try:
        cabecalho = pd.read_csv(io.BytesIO(conteudo), sep=";", encoding="latin1", nrows=0)
    except Exception as erro:  # arquivo vazio, binário etc.
        raise ArquivoInvalido(f"Não foi possível ler o arquivo como CSV ({erro}).") from erro

    encontradas = [str(c) for c in cabecalho.columns]
    if len(encontradas) < TAMANHO_MINIMO_COLUNAS:
        raise ArquivoInvalido(
            "O arquivo não parece ser o relatório ESFT0100: as colunas devem ser separadas por "
            "ponto e vírgula (;). Exporte o relatório do ERP novamente em CSV."
        )
    faltando = [c for c in colunas if c not in encontradas]
    if faltando:
        raise ArquivoInvalido(
            "O arquivo não tem todas as colunas do relatório ESFT0100. Faltando: "
            + ", ".join(faltando)
        )

    return pd.read_csv(
        io.BytesIO(conteudo),
        sep=";",
        encoding="latin1",
        usecols=colunas,
        dtype={"Nota Fiscal": str, "Nro Embarque": str},
        low_memory=False,
    )


def validar_embarques(conteudo: bytes, aba: str = "BASE ESGR0050 POTENCIAL") -> None:
    try:
        abas = pd.ExcelFile(io.BytesIO(conteudo)).sheet_names
    except Exception as erro:
        raise ArquivoInvalido(f"Não foi possível abrir a planilha de embarques ({erro}).") from erro
    if aba not in abas:
        raise ArquivoInvalido(
            f'A planilha de embarques precisa ter a aba "{aba}". Abas encontradas: {", ".join(abas)}'
        )


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------
def fonte_atual() -> Optional[FonteDados]:
    return st.session_state.get(CHAVE_SESSAO)


def trocar_dados() -> None:
    """Descarta os dados carregados (memória e cache) e volta à tela inicial."""
    st.session_state.pop(CHAVE_SESSAO, None)
    st.cache_data.clear()


def obter_fonte(colunas_csv: Iterable[str]) -> FonteDados:
    """
    Devolve a fonte de dados escolhida. Enquanto nenhuma foi escolhida, mostra a
    tela de carregamento e interrompe a execução do restante do dashboard.
    """
    fonte = fonte_atual()
    if fonte is not None:
        return fonte
    _tela_carregamento(list(colunas_csv))
    st.stop()


def _tela_carregamento(colunas_csv: list[str]) -> None:
    ui.cabecalho_pagina(
        "Faturamento",
        "Carregue o relatório de faturamento para abrir o painel.",
    )
    ui.secao(
        "Carregar dados",
        "Os arquivos são processados só neste computador e não ficam salvos: "
        "ao fechar o painel, é preciso carregá-los de novo.",
    )

    col_csv, col_xlsx = st.columns(2)
    with col_csv:
        csv = st.file_uploader(
            "Relatório de faturamento (ESFT0100, .csv)",
            type=["csv"],
            help='Exportação do ERP com colunas separadas por ";". Obrigatório.',
        )
    with col_xlsx:
        xlsx = st.file_uploader(
            "Planilha de embarques (.xlsx) — opcional",
            type=["xlsx"],
            help='Usada na análise de Potencial x Faturamento (aba "BASE ESGR0050 POTENCIAL").',
        )

    abrir = st.button("Abrir painel", type="primary", disabled=csv is None)

    st.caption("Ainda sem os arquivos? Veja como o painel funciona com dados fictícios.")
    demo = st.button("Usar dados de demonstração")

    if demo:
        st.session_state[CHAVE_SESSAO] = FonteDados(tipo="demo")
        st.rerun()

    if abrir and csv is not None:
        conteudo_csv = csv.getvalue()
        conteudo_xlsx = xlsx.getvalue() if xlsx is not None else None
        try:
            with st.spinner("Conferindo os arquivos..."):
                ler_esft0100(conteudo_csv, colunas_csv)  # valida antes de abrir o painel
                if conteudo_xlsx is not None:
                    validar_embarques(conteudo_xlsx)
        except ArquivoInvalido as erro:
            st.error(str(erro))
            return
        st.session_state[CHAVE_SESSAO] = FonteDados(
            tipo="arquivo",
            nome=csv.name,
            csv=conteudo_csv,
            embarques=conteudo_xlsx,
            embarques_nome=xlsx.name if xlsx is not None else "",
            chave=_hash(conteudo_csv, conteudo_xlsx),
        )
        st.rerun()


def resumo_sidebar(fonte: FonteDados) -> None:
    """Bloco no topo da sidebar com a origem dos dados e o botão para trocá-los."""
    st.subheader("Dados")
    if fonte.demonstracao:
        st.caption("Demonstração — dados fictícios")
    else:
        texto = f"**{fonte.nome}**"
        if fonte.embarques_nome:
            texto += f"  \nEmbarques: {fonte.embarques_nome}"
        st.markdown(texto)
    if st.button("Trocar dados", use_container_width=True):
        trocar_dados()
        st.rerun()
