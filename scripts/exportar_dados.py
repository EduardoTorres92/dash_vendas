"""
Exporta os dados do dashboard para JSON, consumido pela versão web (web/).

As regras de negócio continuam no Python: este script carrega os dados com as
mesmas funções de ETL usadas pelo faturamento.py (Streamlit) e grava:

- web/public/data/faturamento.json: notas fiscais consolidadas por
  (NF, marca, data, categoria de receita), cut-offs por mês e totais do mês
  anterior. O frontend só filtra e soma; a fórmula do líquido é a mesma.
- web/tests/fixtures/paridade.json (com --paridade): resultados calculados
  aqui, seguindo passo a passo o faturamento.py, para o teste que garante que
  a versão web chega nos mesmos números.

Uso:
    python scripts/exportar_dados.py [--paridade]
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import importlib.util
import io
import json
import math
import os
import sys

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA_DADOS = os.path.join(RAIZ, "web", "public", "data", "faturamento.json")
SAIDA_PARIDADE = os.path.join(RAIZ, "web", "tests", "fixtures", "paridade.json")

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
         "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
MARCAS_INDESEJADAS = ["?", "MTK CD SP"]  # mesmas de faturamento.py

# Categorias de receita (índices usados no JSON)
CAT_SIM, CAT_NAO, CAT_OUTRA = 0, 1, 2


def _importar(nome):
    if RAIZ not in sys.path:
        sys.path.insert(0, RAIZ)
    spec = importlib.util.spec_from_file_location(nome, os.path.join(RAIZ, f"{nome}.py"))
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@contextlib.contextmanager
def _silencioso():
    """Os ETLs imprimem mensagens de debug; aqui elas só poluem a saída."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def _preparar_datas(df):
    """Mesmo tratamento de data do faturamento.py."""
    if "Dt Emis NF" not in df.columns or df.empty:
        return df
    df = df.copy()
    df["Dt Emis NF"] = pd.to_datetime(df["Dt Emis NF"], format="%d/%m/%y", errors="coerce").dt.normalize()
    return df.dropna(subset=["Dt Emis NF"])


def carregar(etl_fat, etl_dev):
    with _silencioso():
        faturado = etl_fat.carregar_dados_faturamento()
        devolucao = etl_dev.carregar_dados_devolucao()
    completo = _preparar_datas(faturado)  # base do "mês anterior" (sem filtro de marcas indesejadas)

    if "Marca" in faturado.columns:
        faturado = faturado[~faturado["Marca"].isin(MARCAS_INDESEJADAS)]
    if "Marca" in devolucao.columns and len(devolucao) > 0:
        devolucao = devolucao[~devolucao["Marca"].isin(MARCAS_INDESEJADAS)]
    return _preparar_datas(faturado), _preparar_datas(devolucao), completo


def _categoria(tipo_oper, tipos_sim, tipos_nao):
    tipo = tipo_oper.astype(str)
    return pd.Series(CAT_OUTRA, index=tipo.index).mask(tipo.isin(tipos_nao), CAT_NAO).mask(tipo.isin(tipos_sim), CAT_SIM)


def _notas(df, com_categoria, tipos_sim=(), tipos_nao=()):
    """Consolida itens em (NF, marca, data[, categoria]) -> valor, em colunas."""
    vazio = {"nf": [], "marca": [], "data": [], "categoria": [], "valor": []}
    if df.empty or not {"Nota Fiscal", "Marca", "Vl Net Livro", "Dt Emis NF"} <= set(df.columns):
        return vazio
    df = df.dropna(subset=["Nota Fiscal", "Marca"]).copy()
    df["Nota Fiscal"] = df["Nota Fiscal"].astype(str)
    df["Marca"] = df["Marca"].astype(str)
    df["data"] = df["Dt Emis NF"].dt.strftime("%Y-%m-%d")
    df["categoria"] = _categoria(df["Tipo Oper"], tipos_sim, tipos_nao) if com_categoria else CAT_OUTRA
    agrupado = (
        df.groupby(["Nota Fiscal", "Marca", "data", "categoria"])["Vl Net Livro"]
        .sum()
        .reset_index()
    )
    return {
        "nf": agrupado["Nota Fiscal"].tolist(),
        "marca": agrupado["Marca"].tolist(),
        "data": agrupado["data"].tolist(),
        "categoria": agrupado["categoria"].astype(int).tolist(),
        "valor": [round(float(v), 6) for v in agrupado["Vl Net Livro"]],
    }


def _compactar(notas, marcas):
    """Troca marca/data por índices para reduzir o tamanho do JSON."""
    datas = sorted(set(notas["data"]))
    idx_data = {d: i for i, d in enumerate(datas)}
    idx_marca = {m: i for i, m in enumerate(marcas)}
    return {
        "datas": datas,
        "nf": notas["nf"],
        "marca": [idx_marca[m] for m in notas["marca"]],
        "data": [idx_data[d] for d in notas["data"]],
        "categoria": notas["categoria"],
        "valor": notas["valor"],
    }


def exportar(etl_fat, etl_dev):
    faturado, devolucao, completo = carregar(etl_fat, etl_dev)
    tipos_sim = etl_fat.obter_tipos_receita_sim()
    tipos_nao = etl_fat.obter_tipos_receita_nao()

    marcas = sorted(faturado["Marca"].dropna().astype(str).unique())
    meses = sorted(faturado["Dt Emis NF"].dt.to_period("M").astype(str).unique())

    # Totais por marca e mês sobre a base completa, sem deduplicar NFs
    # (é o que calcular_variacoes_mes_anterior_todas_marcas faz)
    completo = completo.dropna(subset=["Marca"])
    totais = (
        completo.assign(mes=completo["Dt Emis NF"].dt.to_period("M").astype(str))
        .groupby(["mes", "Marca"])["Vl Net Livro"].sum()
    )
    totais_mes = {}
    for (mes, marca), valor in totais.items():
        totais_mes.setdefault(mes, {})[str(marca)] = round(float(valor), 6)

    cut_off = {
        mes: {marca: float(etl_fat.obter_cut_off_por_marca_mes(marca, mes)) for marca in marcas}
        for mes in MESES
    }

    marcas_dev = sorted(set(marcas) | set(devolucao["Marca"].dropna().astype(str).unique())) if "Marca" in devolucao.columns else marcas
    return {
        "versao": 1,
        "geradoEm": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "marcas": marcas,
        "marcasDevolucao": marcas_dev,
        "meses": meses,
        "cores": etl_fat.obter_cores_marca(),
        "tiposReceita": {"sim": tipos_sim, "nao": tipos_nao},
        "cutOff": cut_off,
        "totaisMes": totais_mes,
        "faturamento": _compactar(_notas(faturado, True, tipos_sim, tipos_nao), marcas),
        "devolucao": _compactar(_notas(devolucao, False), marcas_dev),
    }


# ---------------------------------------------------------------------------
# Paridade: reproduz a seção "Faturamento líquido por marca" do faturamento.py
# ---------------------------------------------------------------------------
def _mes_anterior(ano, mes):
    return (ano - 1, 12) if mes == 1 else (ano, mes - 1)


def _no_mes(df, ano, mes):
    if df.empty:
        return df
    inicio = datetime.date(ano, mes, 1)
    fim = (datetime.date(ano + 1, 1, 1) if mes == 12 else datetime.date(ano, mes + 1, 1)) - datetime.timedelta(days=1)
    datas = df["Dt Emis NF"].dt.date
    return df[(datas >= inicio) & (datas <= fim)]


def esperado(etl_fat, etl_dev, base, mes, marcas, dia, receita):
    """
    mes: "AAAA-MM" ou None (Todos os Dados); marcas: lista ou None (todas);
    dia: int ou None; receita: "Ambas" | "Sim" | "Não".
    """
    faturado, devolucao, completo = base
    todas = sorted(faturado["Marca"].dropna().unique())

    if mes:
        ano, num = map(int, mes.split("-"))
        faturado = _no_mes(faturado, ano, num)
        devolucao = _no_mes(devolucao, ano, num)
    if marcas and len(marcas) < len(todas):
        faturado = faturado[faturado["Marca"].isin(marcas)]
        if "Marca" in devolucao.columns and len(devolucao) > 0:
            devolucao = devolucao[devolucao["Marca"].isin(marcas)]
    if dia:
        faturado = faturado[faturado["Dt Emis NF"].dt.day == dia]
        if "Dt Emis NF" in devolucao.columns and len(devolucao) > 0:
            devolucao = devolucao[devolucao["Dt Emis NF"].dt.day == dia]
    if receita == "Sim":
        faturado = etl_fat.filtrar_receita_sim(faturado)
    elif receita == "Não":
        faturado = etl_fat.filtrar_receita_nao(faturado)

    with _silencioso():
        por_marca = etl_fat.exibir_cards_faturamento_por_marca_bruto(faturado)
        dev_por_marca = etl_dev.exibir_cards_devolucao_por_marca_bruto(devolucao)
    bruto = dict(zip(por_marca["Marca"], por_marca["Valor"]))
    dev = dict(zip(dev_por_marca["Marca"], dev_por_marca["Valor"]))

    cut, cut_ini, variacoes = {}, {}, {}
    if mes:
        ano, num = map(int, mes.split("-"))
        _, num_ant = _mes_anterior(ano, num)
        for marca in por_marca["Marca"]:
            cut[marca] = etl_fat.obter_cut_off_por_marca_mes(marca, MESES[num - 1])
            cut_ini[marca] = etl_fat.obter_cut_off_por_marca_mes(marca, MESES[num_ant - 1])
        ano_ant, num_ant = _mes_anterior(ano, num)
        anterior = _no_mes(completo, ano_ant, num_ant)
        tot_ant = anterior.groupby("Marca")["Vl Net Livro"].sum() if len(anterior) else pd.Series(dtype=float)
        for marca in por_marca["Marca"]:
            atual, ant = bruto[marca], tot_ant.get(marca, 0)
            if len(anterior) == 0:
                variacoes[marca] = 0.0
            elif ant > 0:
                variacoes[marca] = round((atual - ant) / ant * 100, 1)
            else:
                variacoes[marca] = 100.0 if atual > 0 else 0.0

    total_bruto = sum(bruto.values())
    cards = []
    for marca in por_marca["Marca"]:
        b, d = bruto[marca], dev.get(marca, 0)
        c, ci = cut.get(marca, 0), cut_ini.get(marca, 0)
        cards.append({
            "marca": marca,
            "bruto": b,
            "devolucoes": d,
            "cutOff": c,
            "cutOffInicial": ci,
            "liquido": b + ci - d - c,
            "variacao": variacoes.get(marca, 0.0),
            "participacao": (b / total_bruto * 100) if total_bruto > 0 else 0,
        })
    return cards


def casos_paridade(etl_fat, etl_dev, dados):
    base = carregar(etl_fat, etl_dev)
    marcas = dados["marcas"]
    casos = []
    filtros = [(None, None, None, "Ambas"), (None, None, None, "Sim")]
    for mes in dados["meses"]:
        for receita in ("Ambas", "Sim", "Não"):
            filtros.append((mes, None, None, receita))
    ultimo = dados["meses"][-1]
    filtros += [
        (ultimo, None, 3, "Ambas"),
        (ultimo, None, 7, "Sim"),
        (dados["meses"][0], None, 15, "Não"),
        (ultimo, marcas[:2], None, "Ambas"),
        (ultimo, [m for m in marcas if "SAO PAULO" in m], None, "Sim"),
        (dados["meses"][4], marcas[1:4], 10, "Ambas"),
    ]
    for mes, sel, dia, receita in filtros:
        cards = esperado(etl_fat, etl_dev, base, mes, sel, dia, receita)
        for card in cards:
            for chave, valor in card.items():
                if isinstance(valor, float) and math.isnan(valor):
                    card[chave] = 0.0
        casos.append({
            "filtros": {"mes": mes, "marcas": sel, "dia": dia, "receita": receita},
            "cards": cards,
        })
    return casos


def _gravar(caminho, conteudo):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arq:
        json.dump(conteudo, arq, ensure_ascii=False, separators=(",", ":"))
    return os.path.getsize(caminho)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--paridade", action="store_true", help="gera também os casos do teste de paridade")
    args = parser.parse_args()

    etl_fat = _importar("ETL_faturamento")
    etl_dev = _importar("ETL_devolucao")

    dados = exportar(etl_fat, etl_dev)
    tamanho = _gravar(SAIDA_DADOS, dados)
    print(f"Dados: {os.path.relpath(SAIDA_DADOS, RAIZ)} "
          f"({tamanho / 1024 / 1024:.1f} MB, {len(dados['faturamento']['nf'])} linhas de NF, "
          f"{len(dados['devolucao']['nf'])} de devolução)")

    if args.paridade:
        casos = casos_paridade(etl_fat, etl_dev, dados)
        _gravar(SAIDA_PARIDADE, casos)
        print(f"Paridade: {os.path.relpath(SAIDA_PARIDADE, RAIZ)} ({len(casos)} casos)")


if __name__ == "__main__":
    main()
