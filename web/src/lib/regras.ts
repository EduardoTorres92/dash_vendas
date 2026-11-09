/**
 * Regras de negócio da seção "Faturamento líquido por marca".
 *
 * Porta fiel de faturamento.py (Streamlit) + ETL_faturamento/ETL_devolucao.
 * O teste tests/paridade.test.ts compara estes resultados com os calculados
 * pelo próprio Python (scripts/exportar_dados.py --paridade).
 *
 *   líquido = bruto + cut-off inicial − devoluções − cut-off
 *
 * - Bruto: itens filtrados (mês, marcas, dia, tipo de receita) somados por
 *   (NF, marca); uma NF que aparece em mais de uma marca conta só para a
 *   primeira em ordem alfabética (drop_duplicates após o groupby do pandas).
 * - Devoluções: mesma consolidação, sem o filtro de tipo de receita.
 * - Cut-off: valor fixo do mês selecionado; cut-off inicial: do mês anterior.
 *   Ambos são zero em "Todos os Dados".
 * - Variação: bruto filtrado vs. total do mês anterior inteiro (sem filtros e
 *   sem deduplicar NFs), com 1 casa. Sem base anterior: 100% se houver
 *   faturamento, senão 0%.
 */
import type { CardMarca, DadosFaturamento, Filtros, TabelaNotas } from "./tipos";

export const MESES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

const CATEGORIA_POR_RECEITA = { Sim: 0, "Não": 1 } as const;

/** "2025-10" -> "Outubro/2025" */
export function rotuloMes(mes: string): string {
  const [ano, num] = mes.split("-");
  return `${MESES[Number(num) - 1]}/${ano}`;
}

export function mesAnterior(mes: string): string {
  const [ano, num] = mes.split("-").map(Number);
  return num === 1 ? `${ano - 1}-12` : `${ano}-${String(num - 1).padStart(2, "0")}`;
}

/** Arredonda como o round(x, 1) do Python para os casos usuais. */
function arredondar1(valor: number): number {
  return Number(valor.toFixed(1));
}

/**
 * Soma por marca após consolidar por NF, com o desempate do pandas:
 * groupby(["Nota Fiscal", "Marca"]) ordena as marcas e drop_duplicates
 * mantém a primeira. Como `nomes` está em ordem alfabética, o menor índice
 * é a marca que fica.
 */
function somarPorMarca(
  tabela: TabelaNotas,
  nomes: string[],
  incluir: (i: number) => boolean,
): Map<string, number> {
  const porNota = new Map<string, Map<number, number>>();
  for (let i = 0; i < tabela.nf.length; i++) {
    if (!incluir(i)) continue;
    let marcas = porNota.get(tabela.nf[i]);
    if (!marcas) {
      marcas = new Map();
      porNota.set(tabela.nf[i], marcas);
    }
    const m = tabela.marca[i];
    marcas.set(m, (marcas.get(m) ?? 0) + tabela.valor[i]);
  }

  const total = new Map<string, number>();
  for (const marcas of porNota.values()) {
    let escolhida = Infinity;
    for (const m of marcas.keys()) if (m < escolhida) escolhida = m;
    const nome = nomes[escolhida];
    total.set(nome, (total.get(nome) ?? 0) + marcas.get(escolhida)!);
  }
  return total;
}

function filtroLinhas(tabela: TabelaNotas, nomes: string[], filtros: Filtros, todas: number, comReceita: boolean) {
  const datasOk = tabela.datas.map((data) => {
    if (filtros.mes && data.slice(0, 7) !== filtros.mes) return false;
    if (filtros.dia && Number(data.slice(8, 10)) !== filtros.dia) return false;
    return true;
  });
  const filtraMarcas = filtros.marcas !== null && filtros.marcas.length < todas;
  const marcasOk = new Set(filtraMarcas ? filtros.marcas : nomes);
  const marcaOk = nomes.map((nome) => marcasOk.has(nome));
  const categoria = comReceita && filtros.receita !== "Ambas" ? CATEGORIA_POR_RECEITA[filtros.receita] : null;

  return (i: number) =>
    datasOk[tabela.data[i]] &&
    marcaOk[tabela.marca[i]] &&
    (categoria === null || tabela.categoria[i] === categoria);
}

export function calcularCards(dados: DadosFaturamento, filtros: Filtros): CardMarca[] {
  const todas = dados.marcas.length;
  const bruto = somarPorMarca(
    dados.faturamento,
    dados.marcas,
    filtroLinhas(dados.faturamento, dados.marcas, filtros, todas, true),
  );
  const devolucoes = somarPorMarca(
    dados.devolucao,
    dados.marcasDevolucao,
    filtroLinhas(dados.devolucao, dados.marcasDevolucao, filtros, todas, false),
  );

  let cutOff: Record<string, number> = {};
  let cutOffInicial: Record<string, number> = {};
  let totaisAnteriores: Record<string, number> | null = null;
  if (filtros.mes) {
    const anterior = mesAnterior(filtros.mes);
    cutOff = dados.cutOff[MESES[Number(filtros.mes.slice(5, 7)) - 1]] ?? {};
    cutOffInicial = dados.cutOff[MESES[Number(anterior.slice(5, 7)) - 1]] ?? {};
    const totais = dados.totaisMes[anterior];
    totaisAnteriores = totais && Object.keys(totais).length > 0 ? totais : null;
  }

  const totalBruto = [...bruto.values()].reduce((a, b) => a + b, 0);

  return [...bruto.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([marca, valorBruto]) => {
      const devolvido = devolucoes.get(marca) ?? 0;
      const corte = cutOff[marca] ?? 0;
      const corteInicial = cutOffInicial[marca] ?? 0;

      let variacao = 0;
      if (totaisAnteriores) {
        const anterior = totaisAnteriores[marca] ?? 0;
        if (anterior > 0) variacao = arredondar1(((valorBruto - anterior) / anterior) * 100);
        else variacao = valorBruto > 0 ? 100 : 0;
      }

      return {
        marca,
        bruto: valorBruto,
        devolucoes: devolvido,
        cutOff: corte,
        cutOffInicial: corteInicial,
        liquido: valorBruto + corteInicial - devolvido - corte,
        variacao,
        participacao: totalBruto > 0 ? (valorBruto / totalBruto) * 100 : 0,
      };
    });
}
