const moeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const percentual1 = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

/** R$ 1.234,56 */
export const formatarMoeda = (valor: number): string => moeda.format(valor);

/** 12,3% (valor na escala 0–100) */
export const formatarPercentual = (valor: number): string => `${percentual1.format(valor)}%`;

/** +12,3% / −4,5% */
export const formatarVariacao = (valor: number): string =>
  `${valor >= 0 ? "+" : "−"}${percentual1.format(Math.abs(valor))}%`;
