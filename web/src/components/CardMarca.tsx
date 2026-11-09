import type { CSSProperties } from "react";
import { formatarMoeda, formatarPercentual, formatarVariacao } from "../lib/formatos";
import type { CardMarca as Card } from "../lib/tipos";

interface Props {
  card: Card;
  cor: string;
  /** Sem mês anterior para comparar (filtro "Todos os Dados"). */
  semComparacao: boolean;
}

export function CardMarca({ card, cor, semComparacao }: Props) {
  const classe = semComparacao ? "neutro" : card.variacao >= 0 ? "pos" : "neg";
  const seta = semComparacao ? "–" : card.variacao >= 0 ? "▲" : "▼";
  const descricao = semComparacao
    ? "sem comparação com mês anterior"
    : `${card.variacao >= 0 ? "alta" : "queda"} de ${formatarPercentual(Math.abs(card.variacao))} vs mês anterior`;

  return (
    <li className="kpi" style={{ "--cor": cor } as CSSProperties}>
      <h3 className="kpi-rotulo" title={card.marca}>
        <i aria-hidden="true" />
        {card.marca}
      </h3>
      <p className="kpi-valor" title={formatarMoeda(card.liquido)}>
        <span className="sr-only">Faturamento líquido: </span>
        {formatarMoeda(card.liquido)}
      </p>
      <span className={`delta ${classe}`} aria-label={descricao}>
        <span aria-hidden="true">
          {seta} {semComparacao ? "" : formatarVariacao(card.variacao)}
        </span>
        <small aria-hidden="true">{semComparacao ? "sem comparação" : "vs mês anterior"}</small>
      </span>
      <dl className="kpi-detalhes">
        <dt>Bruto</dt>
        <dd>{formatarMoeda(card.bruto)}</dd>
        <dt>Participação no bruto</dt>
        <dd>{formatarPercentual(card.participacao)}</dd>
        <dt>Cut-off inicial</dt>
        <dd>{formatarMoeda(card.cutOffInicial)}</dd>
        <dt>Cut-off</dt>
        <dd>{formatarMoeda(card.cutOff)}</dd>
        <dt>Devoluções</dt>
        <dd>{formatarMoeda(card.devolucoes)}</dd>
      </dl>
    </li>
  );
}
