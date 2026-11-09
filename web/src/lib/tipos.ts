/** Formato de web/public/data/faturamento.json (gerado por scripts/exportar_dados.py). */

/** Notas fiscais consolidadas por (NF, marca, data, categoria), em colunas. */
export interface TabelaNotas {
  /** Datas ISO (AAAA-MM-DD) referenciadas por índice em `data`. */
  datas: string[];
  nf: string[];
  /** Índice em `marcas` (faturamento) ou `marcasDevolucao` (devolução). */
  marca: number[];
  data: number[];
  /** 0 = receita Sim, 1 = receita Não, 2 = outras operações. */
  categoria: number[];
  valor: number[];
}

export interface DadosFaturamento {
  versao: number;
  geradoEm: string;
  marcas: string[];
  marcasDevolucao: string[];
  /** Meses com dados, "AAAA-MM", em ordem. */
  meses: string[];
  cores: Record<string, string>;
  tiposReceita: { sim: string[]; nao: string[] };
  /** Cut-off por nome do mês (Janeiro…Dezembro) e marca. */
  cutOff: Record<string, Record<string, number>>;
  /** Total bruto por mês ("AAAA-MM") e marca, sem deduplicar NFs. */
  totaisMes: Record<string, Record<string, number>>;
  faturamento: TabelaNotas;
  devolucao: TabelaNotas;
}

export type TipoReceita = "Ambas" | "Sim" | "Não";

export interface Filtros {
  /** "AAAA-MM" ou null para "Todos os Dados". */
  mes: string | null;
  /** Marcas selecionadas; null = todas. */
  marcas: string[] | null;
  /** Dia do mês (1–31) ou null para todos. */
  dia: number | null;
  receita: TipoReceita;
}

export interface CardMarca {
  marca: string;
  bruto: number;
  devolucoes: number;
  cutOff: number;
  cutOffInicial: number;
  liquido: number;
  /** Variação % do bruto vs. mês anterior, com 1 casa. */
  variacao: number;
  /** Participação % no bruto total do filtro. */
  participacao: number;
}
