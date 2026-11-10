"""
Mapa do faturamento por estado com MapLibre GL JS (2D e 3D).

O MapLibre e a malha dos estados ficam em static/ e são servidos pelo próprio
Streamlit (server.enableStaticServing), então o mapa funciona sem internet,
sem servidor de mapas e sem chave de acesso. Os dados do relatório também não
saem do computador: vão do Python direto para o navegador local.
"""

from __future__ import annotations

import mimetypes

import pandas as pd
import streamlit as st

# No Windows, o registro às vezes associa .js/.mjs a text/plain, e o navegador
# recusa carregar o MapLibre como módulo. Fixa os tipos certos para o servidor.
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/json", ".json")

NOMES_UF = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins",
}

# Escala sequencial de um tom (validada para daltonismo), clara e escura
ESCALA_CLARA = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281"]
ESCALA_ESCURA = ["#0d366b", "#184f95", "#256abf", "#3987e5", "#6da7ec", "#b7d3f6"]

_HTML = """
<div class="mapa-raiz">
  <link rel="stylesheet" href="/app/static/maplibre/maplibre-gl.css" />
  <div class="barra">
    <div class="segmentado" role="group" aria-label="Visualização do mapa">
      <button type="button" data-modo="2d" aria-pressed="true">2D</button>
      <button type="button" data-modo="3d" aria-pressed="false">3D</button>
    </div>
    <button type="button" class="botao" data-acao="recentrar">Recentrar</button>
    <span class="dica-uso">Ctrl + rolagem para zoom · botão direito para girar e inclinar</span>
  </div>
  <div class="caixa">
    <div class="mapa" role="region" aria-label="Mapa interativo do faturamento por estado. Os mesmos dados estão na tabela ao lado."></div>
    <div class="aviso">Carregando mapa…</div>
    <div class="dica" hidden></div>
  </div>
  <div class="rodape">
    <div class="escala" aria-hidden="true"></div>
    <span class="fixado" role="status"></span>
  </div>
</div>
"""

_CSS = """
.mapa-raiz { font-family: var(--st-font, sans-serif); color: var(--st-text-color); }
.barra { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 8px; }
.segmentado { display: inline-flex; padding: 2px; border: 1px solid var(--st-border-color);
  border-radius: 8px; background: var(--st-secondary-background-color); }
.segmentado button { min-width: 44px; min-height: 32px; padding: 4px 10px; border: 0; border-radius: 6px;
  background: transparent; font: inherit; font-size: 13px; font-weight: 600; color: inherit; opacity: .7; cursor: pointer; }
.segmentado button[aria-pressed="true"] { background: var(--st-background-color); color: var(--st-primary-color);
  opacity: 1; box-shadow: 0 1px 2px rgba(15, 23, 42, .08); }
.botao { min-height: 36px; padding: 4px 12px; border: 1px solid var(--st-border-color); border-radius: 8px;
  background: var(--st-background-color); color: inherit; font: inherit; font-size: 13px; cursor: pointer; }
.botao:hover { background: var(--st-secondary-background-color); }
button:focus-visible { outline: 2px solid var(--st-primary-color); outline-offset: 1px; }
.dica-uso { margin-left: auto; font-size: 12px; opacity: .65; }
.caixa { position: relative; }
.mapa { height: 520px; border-radius: 8px; overflow: hidden; }
[hidden] { display: none !important; }
.aviso { position: absolute; inset: 0; display: grid; place-items: center; font-size: 13px; opacity: .7; }
.dica { position: absolute; z-index: 5; pointer-events: none; min-width: 170px; padding: 10px 12px; border-radius: 8px;
  background: var(--st-text-color); color: var(--st-background-color); font-size: 12px; line-height: 1.45;
  box-shadow: 0 6px 18px rgba(15, 23, 42, .18); transform: translate(-50%, calc(-100% - 12px)); }
.dica b { font-size: 13px; font-variant-numeric: tabular-nums; }
.dica .titulo { opacity: .75; margin-bottom: 4px; }
.rodape { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px;
  margin-top: 10px; font-size: 12px; }
.escala { display: flex; align-items: center; gap: 6px; }
.escala i { width: 22px; height: 10px; border-radius: 2px; }
.fixado:not(:empty) { display: inline-flex; align-items: center; gap: 6px; padding: 2px 4px 2px 10px; border-radius: 999px;
  background: var(--st-secondary-background-color); font-variant-numeric: tabular-nums; }
.fixado button { width: 24px; height: 24px; border: 0; border-radius: 999px; background: transparent; color: inherit;
  font-size: 16px; cursor: pointer; }
.maplibregl-ctrl-group { background: var(--st-background-color); }
.escuro .maplibregl-ctrl-icon { filter: invert(1); }
"""

_JS = """
const BRASIL = [[-74.2, -33.9], [-34.6, 5.4]];
const ALTURA_MAXIMA = 650000;
const instancias = new WeakMap();
// O módulo do componente não tem URL própria: os endereços precisam ser absolutos
const ESTATICO = new URL("/app/static/", window.location.origin).href;

const moeda = (v) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const compacta = (v) => v >= 1e6 ? `R$ ${(v / 1e6).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} mi`
  : v >= 1e3 ? `R$ ${Math.round(v / 1e3).toLocaleString("pt-BR")} mil` : moeda(v);
const inteiro = (v) => Math.round(v).toLocaleString("pt-BR");
const pct = (v) => `${v.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;

function camera(mapa, modo3d) {
  const angulos = { pitch: modo3d ? 52 : 0, bearing: modo3d ? -18 : 0 };
  const base = mapa.cameraForBounds(BRASIL, { padding: 16, ...angulos });
  return { center: base?.center ?? [-53, -14.5], zoom: (base?.zoom ?? 3) + (modo3d ? 0.35 : 0), ...angulos };
}

function comValores(malha, data) {
  const porUf = new Map(data.estados.map((e) => [e.uf, e]));
  const faixas = data.escala;
  return { type: "FeatureCollection", features: malha.features.map((f) => {
    const e = porUf.get(f.properties.uf);
    const faixa = e ? Math.min(6, Math.max(1, Math.ceil((e.valor / data.maior) * 6))) : 0;
    return { ...f, properties: { ...f.properties,
      cor: faixa ? faixas[faixa - 1] : data.vazio,
      corTexto: faixa === 0 ? data.textoFraco : (faixa <= 3) === !data.escuro ? "#0b0b0b" : "#ffffff",
      altura: e ? Math.max(8000, (e.valor / data.maior) * ALTURA_MAXIMA) : 0 } };
  }) };
}

function desenharDados(inst) {
  const { mapa, malha, data, raiz } = inst;
  raiz.querySelector(".mapa-raiz").classList.toggle("escuro", data.escuro);
  mapa.setPaintProperty("fundo", "background-color", data.fundo);
  mapa.setPaintProperty("contorno", "line-color", ["case", ["any",
    ["boolean", ["feature-state", "hover"], false], ["boolean", ["feature-state", "fixado"], false]],
    data.destaque, data.fundo]);
  mapa.getSource("estados").setData(comValores(malha.estados, data));
  mapa.getSource("rotulos").setData(comValores(malha.rotulos, data));
  raiz.querySelector(".escala").innerHTML = `<span>0</span>${data.escala.map((c) => `<i style="background:${c}"></i>`).join("")}<span>${compacta(data.maior)}</span>`
    + (data.exterior ? `<span style="margin-left:12px">Exterior: <b>${compacta(data.exterior)}</b></span>` : "");
  mostrarFixado(inst);
}

function mostrarFixado(inst) {
  const alvo = inst.raiz.querySelector(".fixado");
  if (!inst.fixado) { alvo.innerHTML = ""; return; }
  const e = inst.data.estados.find((x) => x.uf === inst.fixado);
  const nome = inst.data.nomes[inst.fixado] ?? inst.fixado;
  alvo.innerHTML = e
    ? `<b>${nome}</b> · ${moeda(e.valor)} · ${pct(e.pct)} · ${inteiro(e.notas)} NFs`
    : `<b>${nome}</b> · sem faturamento no período`;
  const fechar = document.createElement("button");
  fechar.type = "button"; fechar.textContent = "×"; fechar.setAttribute("aria-label", "Limpar estado selecionado");
  fechar.onclick = () => fixar(inst, null);
  alvo.appendChild(fechar);
}

function fixar(inst, uf) {
  if (inst.fixado) inst.mapa.setFeatureState({ source: "estados", id: inst.fixado }, { fixado: false });
  inst.fixado = uf;
  if (uf) inst.mapa.setFeatureState({ source: "estados", id: uf }, { fixado: true });
  mostrarFixado(inst);
}

function trocarModo(inst, modo3d) {
  inst.modo3d = modo3d;
  inst.raiz.querySelectorAll("[data-modo]").forEach((b) => b.setAttribute("aria-pressed", String((b.dataset.modo === "3d") === modo3d)));
  inst.mapa.setLayoutProperty("estados-3d", "visibility", modo3d ? "visible" : "none");
  inst.mapa.setLayoutProperty("siglas", "visibility", modo3d ? "none" : "visible");
  inst.mapa.easeTo({ ...camera(inst.mapa, modo3d), duration: 900 });
}

async function criar(raiz, data) {
  const inst = { raiz, data, modo3d: false, fixado: null, pronto: false };
  instancias.set(raiz, inst);
  const [gl, estados, rotulos] = await Promise.all([
    import(`${ESTATICO}maplibre/maplibre-gl.mjs`),
    fetch(`${ESTATICO}geo/brasil-uf.json`).then((r) => r.json()),
    fetch(`${ESTATICO}geo/brasil-uf-rotulos.json`).then((r) => r.json()),
  ]);
  inst.malha = { estados, rotulos };
  const mapa = new gl.Map({
    container: raiz.querySelector(".mapa"),
    style: { version: 8, sources: {}, layers: [{ id: "fundo", type: "background", paint: { "background-color": data.fundo } }] },
    bounds: BRASIL, fitBoundsOptions: { padding: 12 }, maxBounds: [[-100, -50], [-10, 20]],
    minZoom: 2, maxZoom: 8, maxPitch: 65, attributionControl: false, cooperativeGestures: true,
    locale: {
      "NavigationControl.ZoomIn": "Aproximar", "NavigationControl.ZoomOut": "Afastar",
      "NavigationControl.ResetBearing": "Voltar ao norte",
      "CooperativeGesturesHandler.WindowsHelpText": "Use Ctrl + rolagem para dar zoom no mapa",
      "CooperativeGesturesHandler.MacHelpText": "Use ⌘ + rolagem para dar zoom no mapa",
      "CooperativeGesturesHandler.MobileHelpText": "Use dois dedos para mover o mapa",
    },
  });
  inst.mapa = mapa;
  mapa.addControl(new gl.NavigationControl({ visualizePitch: true }), "top-right");
  mapa.on("load", () => {
    mapa.addSource("estados", { type: "geojson", data: { type: "FeatureCollection", features: [] }, promoteId: "uf" });
    mapa.addSource("rotulos", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
    mapa.addLayer({ id: "estados-cor", type: "fill", source: "estados", paint: { "fill-color": ["get", "cor"] } });
    mapa.addLayer({ id: "contorno", type: "line", source: "estados", paint: {
      "line-color": inst.data.fundo,
      "line-width": ["case", ["any", ["boolean", ["feature-state", "hover"], false],
        ["boolean", ["feature-state", "fixado"], false]], 2.5, 0.8] } });
    mapa.addLayer({ id: "estados-3d", type: "fill-extrusion", source: "estados", layout: { visibility: "none" },
      paint: { "fill-extrusion-color": ["get", "cor"], "fill-extrusion-height": ["get", "altura"],
               "fill-extrusion-opacity": 0.92, "fill-extrusion-vertical-gradient": true } });
    mapa.addLayer({ id: "siglas", type: "symbol", source: "rotulos",
      layout: { "text-field": ["get", "uf"], "text-size": 11 }, paint: { "text-color": ["get", "corTexto"] } });
    inst.pronto = true;
    raiz.querySelector(".aviso").hidden = true;
    desenharDados(inst);
  });

  const dica = raiz.querySelector(".dica");
  let emFoco = null;
  const marcar = (uf) => {
    if (emFoco === uf) return;
    if (emFoco) mapa.setFeatureState({ source: "estados", id: emFoco }, { hover: false });
    emFoco = uf;
    if (uf) mapa.setFeatureState({ source: "estados", id: uf }, { hover: true });
  };
  for (const camada of ["estados-cor", "estados-3d"]) {
    mapa.on("mousemove", camada, (ev) => {
      const uf = ev.features?.[0]?.properties?.uf;
      if (!uf) return;
      marcar(uf);
      mapa.getCanvas().style.cursor = "pointer";
      const e = inst.data.estados.find((x) => x.uf === uf);
      const nome = inst.data.nomes[uf] ?? uf;
      dica.innerHTML = e
        ? `<div class="titulo">${nome}</div><div><b>${moeda(e.valor)}</b> faturamento</div><div><b>${pct(e.pct)}</b> do total</div><div><b>${inteiro(e.notas)}</b> NFs · <b>${inteiro(e.quantidade)}</b> itens</div>`
        : `<div class="titulo">${nome}</div><div>Sem faturamento no período</div>`;
      dica.style.left = `${ev.point.x}px`;
      dica.style.top = `${ev.point.y}px`;
      dica.hidden = false;
    });
    mapa.on("mouseleave", camada, () => { marcar(null); mapa.getCanvas().style.cursor = ""; dica.hidden = true; });
    mapa.on("click", camada, (ev) => {
      const uf = ev.features?.[0]?.properties?.uf;
      if (uf) fixar(inst, inst.fixado === uf ? null : uf);
    });
  }
  raiz.querySelectorAll("[data-modo]").forEach((b) => { b.onclick = () => inst.pronto && trocarModo(inst, b.dataset.modo === "3d"); });
  raiz.querySelector("[data-acao=recentrar]").onclick = () => inst.pronto && mapa.easeTo({ ...camera(mapa, inst.modo3d), duration: 700 });
  return inst;
}

export default function (component) {
  const { data, parentElement } = component;
  const existente = instancias.get(parentElement);
  if (existente) {
    existente.data = data;
    if (existente.pronto) desenharDados(existente);
    return;
  }
  criar(parentElement, data).catch((erro) => {
    const aviso = parentElement.querySelector(".aviso");
    if (aviso) aviso.textContent = `Não foi possível abrir o mapa (${erro?.message ?? erro}). Os valores estão na tabela ao lado.`;
  });
  return () => {
    instancias.get(parentElement)?.mapa?.remove();
    instancias.delete(parentElement);
  };
}
"""

_COMPONENTE = st.components.v2.component("dash_vendas_mapa_estados", html=_HTML, css=_CSS, js=_JS)


def mapa_estados(estados: pd.DataFrame, *, key: str = "mapa_estados") -> None:
    """
    Desenha o mapa a partir de um DataFrame com as colunas 'Estado' (sigla),
    'Valor Total', 'Qtd NFs' e 'Qtd Total'. Vendas para o exterior (EX) ficam
    fora do mapa e aparecem na legenda.
    """
    df = estados.copy()
    df["Estado"] = df["Estado"].astype(str).str.strip().str.upper()
    df = df.groupby("Estado", as_index=False)[["Valor Total", "Qtd NFs", "Qtd Total"]].sum()
    total = float(df["Valor Total"].sum()) or 1.0
    nacionais = df[df["Estado"].isin(NOMES_UF.keys())]
    exterior = float(df.loc[~df["Estado"].isin(NOMES_UF.keys()), "Valor Total"].sum())

    escuro = getattr(st.context.theme, "type", "light") == "dark"
    data = {
        "estados": [
            {"uf": uf, "valor": float(valor), "notas": int(notas), "quantidade": float(qtd), "pct": float(valor) / total * 100}
            for uf, valor, notas, qtd in zip(
                nacionais["Estado"], nacionais["Valor Total"], nacionais["Qtd NFs"], nacionais["Qtd Total"]
            )
        ],
        "maior": float(nacionais["Valor Total"].max()) if len(nacionais) else 1.0,
        "exterior": exterior,
        "nomes": NOMES_UF,
        "escuro": escuro,
        "escala": ESCALA_ESCURA if escuro else ESCALA_CLARA,
        "fundo": "#0e1117" if escuro else "#ffffff",
        "vazio": "#262730" if escuro else "#f1f5f9",
        "destaque": "#fafafa" if escuro else "#0f172a",
        "textoFraco": "#a3a8b8" if escuro else "#64748b",
    }
    _COMPONENTE(data=data, key=key, height=620)
