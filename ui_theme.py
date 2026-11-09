"""
Design system do dashboard de faturamento.

Direção visual gerada com a skill UI/UX Pro Max
(produto: "Analytics Dashboard" / "Financial Dashboard"):

- Estilo: Data-Dense Dashboard + Minimal Swiss (grid enxuto, cards compactos,
  máxima visibilidade de dados, sem ornamentos).
- Paleta: azul de dados (#1E40AF / #3B82F6) com destaque âmbar (#D97706),
  fundo neutro (#F8FAFC), positivo #059669, negativo #DC2626.
- Tipografia: Fira Sans (rótulos e texto) + Fira Code (números, tabular).
- Regras aplicadas: contraste mínimo 4.5:1, sem emoji como ícone, cor nunca é
  o único portador de significado (setas ▲/▼ + texto), transições curtas e
  respeito a prefers-reduced-motion.
"""

import functools
from html import escape

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
CORES = {
    "primaria": "#1E40AF",
    "primaria_clara": "#3B82F6",
    "destaque": "#D97706",
    "fundo": "#F8FAFC",
    "superficie": "#FFFFFF",
    "superficie_suave": "#F1F5F9",
    "borda": "#E2E8F0",
    "texto": "#0F172A",
    "texto_suave": "#475569",
    "texto_fraco": "#64748B",
    "positivo": "#059669",
    "positivo_fundo": "#ECFDF5",
    "negativo": "#DC2626",
    "negativo_fundo": "#FEF2F2",
    "alerta": "#D97706",
    "alerta_fundo": "#FFFBEB",
}

# Sequência categórica (distinguível, contraste >= 3:1 sobre branco)
SEQUENCIA_CATEGORICA = [
    "#1E40AF",  # azul
    "#D97706",  # âmbar
    "#059669",  # verde
    "#7C3AED",  # violeta
    "#DC2626",  # vermelho
    "#0891B2",  # ciano
    "#DB2777",  # magenta
    "#475569",  # ardósia
    "#65A30D",  # oliva
    "#9333EA",  # roxo
]

FONTE_TEXTO = "'Fira Sans', 'Segoe UI', system-ui, sans-serif"
FONTE_NUMEROS = "'Fira Code', ui-monospace, 'SFMono-Regular', monospace"


# ---------------------------------------------------------------------------
# Plotly
# ---------------------------------------------------------------------------
def registrar_template_plotly():
    """Registra e ativa o template 'dash_vendas' como padrão do Plotly."""
    eixo = dict(
        showgrid=True,
        gridcolor=CORES["borda"],
        gridwidth=1,
        zeroline=False,
        linecolor=CORES["borda"],
        tickcolor=CORES["borda"],
        ticks="",
        title=dict(font=dict(size=12, color=CORES["texto_suave"])),
        tickfont=dict(size=11, color=CORES["texto_suave"]),
        automargin=True,
    )
    template = go.layout.Template(
        layout=go.Layout(
            font=dict(family=FONTE_TEXTO, size=12, color=CORES["texto"]),
            title=dict(
                font=dict(family=FONTE_TEXTO, size=15, color=CORES["texto"], weight=600),
                x=0,
                xanchor="left",
                pad=dict(l=4, t=4),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=SEQUENCIA_CATEGORICA,
            xaxis={**eixo, "showgrid": False},
            yaxis=eixo,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.01,
                bgcolor="rgba(0,0,0,0)",
                font=dict(size=11, color=CORES["texto_suave"]),
                title=dict(text=""),
            ),
            hoverlabel=dict(
                bgcolor=CORES["texto"],
                bordercolor=CORES["texto"],
                font=dict(family=FONTE_TEXTO, size=12, color="#FFFFFF"),
            ),
            margin=dict(l=8, r=8, t=56, b=8),
            bargap=0.28,
            separators=",.",
        ),
        data=dict(
            bar=[go.Bar(marker=dict(line=dict(width=0)))],
            pie=[
                go.Pie(
                    marker=dict(line=dict(color="#FFFFFF", width=2)),
                    textfont=dict(family=FONTE_TEXTO),
                )
            ],
            scatter=[go.Scatter(line=dict(width=2.5), marker=dict(size=7))],
        ),
    )
    pio.templates["dash_vendas"] = template
    pio.templates.default = "plotly_white+dash_vendas"


# ---------------------------------------------------------------------------
# CSS global
# ---------------------------------------------------------------------------
_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Fira+Sans:wght@400;500;600;700&display=swap');

:root {{
  --dv-primaria: {CORES['primaria']};
  --dv-destaque: {CORES['destaque']};
  --dv-fundo: {CORES['fundo']};
  --dv-superficie: {CORES['superficie']};
  --dv-superficie-suave: {CORES['superficie_suave']};
  --dv-borda: {CORES['borda']};
  --dv-texto: {CORES['texto']};
  --dv-texto-suave: {CORES['texto_suave']};
  --dv-texto-fraco: {CORES['texto_fraco']};
  --dv-positivo: {CORES['positivo']};
  --dv-negativo: {CORES['negativo']};
  --dv-raio: 10px;
  --dv-sombra: 0 1px 2px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.06);
  --dv-sombra-hover: 0 4px 12px rgba(15, 23, 42, 0.08);
  --dv-fonte: {FONTE_TEXTO};
  --dv-fonte-num: {FONTE_NUMEROS};
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
.stMarkdown, .stText, button, input, textarea, select {{
  font-family: var(--dv-fonte);
}}

/* Ícones Material do Streamlit precisam manter a própria fonte */
[data-testid="stIconMaterial"], .material-symbols-rounded {{
  font-family: 'Material Symbols Rounded' !important;
}}

/* ---------- Estrutura ---------- */
[data-testid="stAppViewContainer"] {{ background: var(--dv-fundo); }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container, [data-testid="stMainBlockContainer"] {{
  padding-top: 2rem;
  padding-bottom: 4rem;
  max-width: 1600px;
}}

/* ---------- Tipografia ---------- */
h1, h2, h3, h4 {{
  font-family: var(--dv-fonte) !important;
  color: var(--dv-texto);
  letter-spacing: -0.01em;
}}
h1 {{ font-weight: 700 !important; }}
[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3 {{
  font-size: 1.125rem !important;
  font-weight: 600 !important;
  padding: 0.75rem 0 0.5rem 0 !important;
}}
[data-testid="stHeading"] h3 {{
  font-size: 1rem !important;
  color: var(--dv-texto-suave);
}}
p, li {{ line-height: 1.5; }}
hr {{ border-color: var(--dv-borda) !important; margin: 1.25rem 0 !important; }}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
  background: var(--dv-superficie);
  border-right: 1px solid var(--dv-borda);
}}
[data-testid="stSidebar"] [data-testid="stHeading"] h3 {{
  font-size: 0.75rem !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--dv-texto-fraco);
  padding: 0.25rem 0 !important;
}}
[data-testid="stSidebar"] hr {{ margin: 0.75rem 0 !important; }}
[data-testid="stSidebar"] label p {{
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--dv-texto-suave);
}}
.dv-sidebar-marca {{
  display: flex; align-items: center; gap: 10px;
  padding: 4px 0 12px 0;
}}
.dv-sidebar-marca .dv-logo {{
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--dv-primaria); color: #fff;
  display: grid; place-items: center;
  font-family: var(--dv-fonte-num); font-weight: 600; font-size: 14px;
}}
.dv-sidebar-marca strong {{ display: block; font-size: 15px; color: var(--dv-texto); }}
.dv-sidebar-marca span {{ font-size: 12px; color: var(--dv-texto-fraco); }}

/* ---------- Abas (segmented control) ---------- */
.stTabs [role="tablist"] {{
  gap: 4px;
  background: var(--dv-superficie-suave);
  padding: 4px;
  border-radius: 10px;
  border: 1px solid var(--dv-borda);
  width: fit-content;
  max-width: 100%;
  overflow-x: auto;
}}
.stTabs [role="tab"] {{
  height: 36px;
  margin: 0 !important;
  padding: 0 14px !important;
  border-radius: 7px;
  border: none !important;
  background: transparent;
  color: var(--dv-texto-suave);
  transition: background-color 150ms ease, color 150ms ease;
}}
.stTabs [role="tab"] p {{ font-size: 0.875rem; font-weight: 500; white-space: nowrap; }}
.stTabs [role="tab"]:hover {{ color: var(--dv-texto); }}
.stTabs [role="tab"]:focus-visible {{ outline: 2px solid var(--dv-primaria); outline-offset: 1px; }}
.stTabs [role="tab"][aria-selected="true"] {{
  background: var(--dv-superficie) !important;
  color: var(--dv-primaria) !important;
  box-shadow: var(--dv-sombra);
}}
.stTabs [role="tab"][aria-selected="true"] p {{ font-weight: 600; }}
.stTabs [role="tablist"] > :not([role="tab"]) {{ display: none; }}
.stTabs [role="tabpanel"] {{ padding-top: 0.75rem; }}

/* ---------- Gráficos, tabelas e métricas como cards ---------- */
[data-testid="stPlotlyChart"] {{
  background: var(--dv-superficie);
  border: 1px solid var(--dv-borda);
  border-radius: var(--dv-raio);
  padding: 8px 8px 4px 8px;
  box-shadow: var(--dv-sombra);
}}
[data-testid="stDataFrame"], [data-testid="stTable"] {{
  border: 1px solid var(--dv-borda);
  border-radius: var(--dv-raio);
  overflow: hidden;
  box-shadow: var(--dv-sombra);
  background: var(--dv-superficie);
}}
[data-testid="stMetric"] {{
  background: var(--dv-superficie);
  border: 1px solid var(--dv-borda);
  border-radius: var(--dv-raio);
  padding: 14px 16px;
  box-shadow: var(--dv-sombra);
}}
[data-testid="stMetricLabel"] p {{
  font-size: 0.75rem !important;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--dv-texto-fraco);
  font-weight: 600;
}}
[data-testid="stMetricValue"] {{
  font-family: var(--dv-fonte-num);
  font-size: 1.5rem !important;
  font-weight: 600;
  color: var(--dv-texto);
  font-variant-numeric: tabular-nums;
}}
[data-testid="stExpander"] details {{
  border: 1px solid var(--dv-borda) !important;
  border-radius: var(--dv-raio) !important;
  background: var(--dv-superficie);
}}
[data-testid="stAlert"] {{ border-radius: var(--dv-raio); }}

/* ---------- Cabeçalho da página ---------- */
.dv-header {{
  display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between;
  gap: 16px; padding-bottom: 20px; margin-bottom: 8px;
  border-bottom: 1px solid var(--dv-borda);
}}
.dv-header .dv-eyebrow {{
  font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--dv-primaria); margin: 0 0 4px 0;
}}
.dv-header h1 {{ font-size: 1.75rem !important; margin: 0 !important; padding: 0 !important; line-height: 1.2; }}
.dv-header .dv-sub {{ margin: 6px 0 0 0; color: var(--dv-texto-suave); font-size: 14px; }}
.dv-chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.dv-chip {{
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 10px; border-radius: 999px;
  background: var(--dv-superficie); border: 1px solid var(--dv-borda);
  font-size: 12px; color: var(--dv-texto-suave); white-space: nowrap;
}}
.dv-chip b {{ color: var(--dv-texto); font-weight: 600; }}

/* ---------- Cabeçalho de seção ---------- */
.dv-secao {{
  display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
  margin: 2.25rem 0 0.75rem 0; padding-left: 12px;
  border-left: 3px solid var(--dv-primaria);
}}
.dv-secao h2 {{
  font-size: 1.25rem !important; font-weight: 700 !important;
  margin: 0 !important; padding: 0 !important; line-height: 1.3;
}}
.dv-secao p {{ margin: 2px 0 0 0; color: var(--dv-texto-fraco); font-size: 13px; }}

/* ---------- Cards de KPI ---------- */
.dv-kpi {{
  position: relative;
  background: var(--dv-superficie);
  border: 1px solid var(--dv-borda);
  border-radius: var(--dv-raio);
  padding: 14px 16px 12px 16px;
  margin-bottom: 12px;
  box-shadow: var(--dv-sombra);
  overflow: hidden;
  transition: box-shadow 200ms ease, border-color 200ms ease;
}}
.dv-kpi:hover {{ box-shadow: var(--dv-sombra-hover); border-color: #CBD5E1; }}
.dv-kpi::before {{
  content: ''; position: absolute; inset: 0 0 auto 0; height: 3px;
  background: var(--dv-kpi-cor, var(--dv-primaria));
}}
.dv-kpi-rotulo {{
  display: flex; align-items: center; gap: 8px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--dv-texto-suave);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.dv-kpi-rotulo i {{
  flex: none; width: 8px; height: 8px; border-radius: 2px;
  background: var(--dv-kpi-cor, var(--dv-primaria));
}}
.dv-kpi-valor {{
  font-family: var(--dv-fonte-num); font-variant-numeric: tabular-nums;
  font-size: 1.375rem; letter-spacing: -0.02em; font-weight: 600; color: var(--dv-texto);
  margin: 8px 0 6px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.dv-delta {{
  white-space: nowrap;
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 999px;
  font-family: var(--dv-fonte-num); font-variant-numeric: tabular-nums;
}}
.dv-delta small {{ font-family: var(--dv-fonte); font-weight: 500; opacity: 0.85; }}
.dv-delta.pos {{ color: var(--dv-positivo); background: {CORES['positivo_fundo']}; }}
.dv-delta.neg {{ color: var(--dv-negativo); background: {CORES['negativo_fundo']}; }}
.dv-kpi-detalhes {{
  margin: 12px 0 0 0; padding: 10px 0 0 0;
  border-top: 1px dashed var(--dv-borda);
  display: grid; grid-template-columns: auto 1fr; gap: 4px 12px;
  font-size: 12px; line-height: 1.5;
}}
.dv-kpi-detalhes span {{ font-size: 12px !important; }}
.dv-kpi-detalhes .dt {{ color: var(--dv-texto-fraco); margin: 0; white-space: nowrap; }}
.dv-kpi-detalhes .dd {{
  margin: 0; text-align: right; color: var(--dv-texto);
  font-family: var(--dv-fonte-num); font-variant-numeric: tabular-nums;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.dv-kpi-sub {{ font-size: 12px; color: var(--dv-texto-fraco); }}

/* ---------- Barra de progresso (potencial x faturado) ---------- */
.dv-progresso {{ height: 6px; border-radius: 999px; background: var(--dv-superficie-suave); overflow: hidden; margin-top: 8px; }}
.dv-progresso > span {{ display: block; height: 100%; border-radius: 999px; background: var(--dv-kpi-cor); }}
.dv-status {{ font-size: 11px; font-weight: 600; color: var(--dv-kpi-cor); text-transform: uppercase; letter-spacing: 0.05em; }}

@media (max-width: 640px) {{
  .dv-header h1 {{ font-size: 1.4rem !important; }}
  .block-container, [data-testid="stMainBlockContainer"] {{ padding-left: 1rem; padding-right: 1rem; }}
}}
@media (prefers-reduced-motion: reduce) {{
  * {{ transition: none !important; animation: none !important; }}
}}
</style>
"""


def _usar_template_proprio_nos_graficos():
    """
    Por padrão o st.plotly_chart aplica o tema "streamlit", que sobrescreve o
    template do Plotly (fundo, fontes, grid). Aqui o padrão passa a ser
    theme=None, para que o template 'dash_vendas' seja respeitado. Uma chamada
    que informe `theme` explicitamente continua valendo.
    """
    original = st.plotly_chart
    if getattr(original, "_dash_vendas", False):
        return

    @functools.wraps(original)
    def plotly_chart(*args, **kwargs):
        kwargs.setdefault("theme", None)
        return original(*args, **kwargs)

    plotly_chart._dash_vendas = True
    st.plotly_chart = plotly_chart


def aplicar_tema():
    """Injeta o CSS global e ativa o template Plotly. Chamar logo após set_page_config."""
    registrar_template_plotly()
    _usar_template_proprio_nos_graficos()
    st.markdown(_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Componentes
# ---------------------------------------------------------------------------
def cabecalho_pagina(titulo, subtitulo="", chips=None, eyebrow="Painel comercial"):
    """Cabeçalho principal com título, subtítulo e chips de contexto (filtros ativos)."""
    chips_html = "".join(
        f'<span class="dv-chip">{escape(str(rotulo))} <b>{escape(str(valor))}</b></span>'
        for rotulo, valor in (chips or [])
    )
    st.markdown(
        f"""
        <header class="dv-header">
          <div>
            <p class="dv-eyebrow">{escape(eyebrow)}</p>
            <h1>{escape(titulo)}</h1>
            {f'<p class="dv-sub">{escape(subtitulo)}</p>' if subtitulo else ''}
          </div>
          <div class="dv-chips">{chips_html}</div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def secao(titulo, descricao=""):
    """Título de seção principal (nível 2) com marcador lateral."""
    st.markdown(
        f"""
        <div class="dv-secao"><div>
          <h2>{escape(titulo)}</h2>
          {f'<p>{escape(descricao)}</p>' if descricao else ''}
        </div></div>
        """,
        unsafe_allow_html=True,
    )


def marca_sidebar(titulo="Dash Vendas", subtitulo="Faturamento & devoluções"):
    st.markdown(
        f"""
        <div class="dv-sidebar-marca">
          <div class="dv-logo" aria-hidden="true">DV</div>
          <div><strong>{escape(titulo)}</strong><span>{escape(subtitulo)}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def delta_html(variacao, sufixo="vs mês anterior"):
    """Pílula de variação com seta + sinal (não depende só da cor)."""
    classe = "pos" if variacao >= 0 else "neg"
    seta = "▲" if variacao >= 0 else "▼"
    rotulo = "alta" if variacao >= 0 else "queda"
    return (
        f'<span class="dv-delta {classe}" aria-label="{rotulo} de {abs(variacao):.1f}% {escape(sufixo)}">'
        f'{seta} {f"{variacao:+.1f}".replace(".", ",")}% <small>{escape(sufixo)}</small></span>'
    )


def kpi_card_html(rotulo, valor, cor=None, delta=None, detalhes=None, sub=None):
    """Card de KPI compacto. `detalhes` é uma lista de (rótulo, valor)."""
    estilo = f' style="--dv-kpi-cor:{cor}"' if cor else ""
    linhas = "".join(
        f'<span class="dt">{escape(str(k))}</span><span class="dd" title="{escape(str(v))}">{escape(str(v))}</span>'
        for k, v in (detalhes or [])
    )
    return f"""
    <div class="dv-kpi"{estilo}>
      <div class="dv-kpi-rotulo" title="{escape(str(rotulo))}"><i aria-hidden="true"></i>{escape(str(rotulo))}</div>
      <div class="dv-kpi-valor" title="{escape(str(valor))}">{escape(str(valor))}</div>
      {delta if delta else ''}
      {f'<div class="dv-kpi-sub">{escape(str(sub))}</div>' if sub else ''}
      {f'<div class="dv-kpi-detalhes">{linhas}</div>' if linhas else ''}
    </div>
    """


def progresso_card_html(rotulo, percentual):
    """Card de atingimento de meta com barra de progresso e status textual."""
    if percentual >= 100:
        cor, status = CORES["positivo"], "Meta atingida"
    elif percentual >= 80:
        cor, status = CORES["primaria"], "Próximo da meta"
    elif percentual >= 50:
        cor, status = CORES["alerta"], "Em andamento"
    else:
        cor, status = CORES["negativo"], "Abaixo da meta"
    largura = max(0.0, min(percentual, 100.0))
    return f"""
    <div class="dv-kpi" style="--dv-kpi-cor:{cor}">
      <div class="dv-kpi-rotulo"><i aria-hidden="true"></i>{escape(str(rotulo))}</div>
      <div class="dv-kpi-valor">{f"{percentual:.1f}".replace(".", ",")}%</div>
      <span class="dv-status">{status}</span>
      <div class="dv-progresso" role="progressbar" aria-valuenow="{largura:.0f}" aria-valuemin="0" aria-valuemax="100">
        <span style="width:{largura:.1f}%"></span>
      </div>
    </div>
    """
