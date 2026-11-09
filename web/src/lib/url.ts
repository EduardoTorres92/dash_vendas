/**
 * Filtros <-> query string, para que um link compartilhado abra a mesma visão.
 * Ex.: ?mes=2025-10&marcas=UNIDADE%20SOROCABA,UNIDADE%20CURITIBA&dia=3&receita=Sim
 */
import type { Filtros, TipoReceita } from "./tipos";

const RECEITAS: TipoReceita[] = ["Ambas", "Sim", "Não"];

export function lerFiltrosDaUrl(padrao: Filtros, meses: string[], marcas: string[]): Filtros {
  const p = new URLSearchParams(window.location.search);
  const filtros = { ...padrao };

  const mes = p.get("mes");
  if (mes === "todos") filtros.mes = null;
  else if (mes && meses.includes(mes)) filtros.mes = mes;

  const lista = p.get("marcas")?.split(",").filter((m) => marcas.includes(m));
  if (lista && lista.length > 0 && lista.length < marcas.length) filtros.marcas = lista;

  const dia = Number(p.get("dia"));
  if (Number.isInteger(dia) && dia >= 1 && dia <= 31) filtros.dia = dia;

  const receita = p.get("receita") as TipoReceita | null;
  if (receita && RECEITAS.includes(receita)) filtros.receita = receita;

  return filtros;
}

export function gravarFiltrosNaUrl(filtros: Filtros, mesPadrao: string): void {
  const p = new URLSearchParams();
  if (filtros.mes === null) p.set("mes", "todos");
  else if (filtros.mes !== mesPadrao) p.set("mes", filtros.mes);
  if (filtros.marcas) p.set("marcas", filtros.marcas.join(","));
  if (filtros.dia) p.set("dia", String(filtros.dia));
  if (filtros.receita !== "Ambas") p.set("receita", filtros.receita);
  const busca = p.toString();
  window.history.replaceState(null, "", busca ? `?${busca}` : window.location.pathname);
}
