"""Conversão de datas e números do relatório do ERP (formato brasileiro)."""

import pandas as pd

_ANO_CURTO = r"^\d{1,2}/\d{1,2}/\d{2}$"


def para_data(serie: pd.Series) -> pd.Series:
    """
    Converte datas no formato brasileiro, com ano de 2 ou 4 dígitos
    (24/09/25 ou 24/09/2025), sem nunca trocar dia e mês. Valores que não
    são data viram NaT. Colunas que já são datas só são normalizadas.
    """
    if pd.api.types.is_datetime64_any_dtype(serie):
        return serie.dt.normalize()
    texto = serie.astype("string").str.strip().str.slice(0, 10)
    curto = texto.str.match(_ANO_CURTO, na=False)
    longo = pd.to_datetime(texto.where(~curto), format="%d/%m/%Y", errors="coerce")
    abreviado = pd.to_datetime(texto.where(curto), format="%d/%m/%y", errors="coerce")
    return longo.fillna(abreviado).dt.normalize()


def para_numero(serie: pd.Series) -> pd.Series:
    """
    Converte valores no formato brasileiro (1.930,15) em número. Colunas que o
    pandas já leu como número (arquivos com ponto decimal, como o de
    demonstração) são mantidas como estão, sem remover o ponto.
    """
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype(float)
    texto = serie.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce")
