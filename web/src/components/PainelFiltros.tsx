import { useId, useState } from "react";
import { rotuloMes } from "../lib/regras";
import type { Filtros, TipoReceita } from "../lib/tipos";

interface Props {
  filtros: Filtros;
  meses: string[];
  marcas: string[];
  cores: Record<string, string>;
  geradoEm: string;
  onChange: (filtros: Filtros) => void;
}

const RECEITAS: { valor: TipoReceita; ajuda: string }[] = [
  { valor: "Ambas", ajuda: "Todos os tipos de operação" },
  { valor: "Sim", ajuda: "Receita direta e revenda" },
  { valor: "Não", ajuda: "Bonificações e transferências" },
];

const dataGeracao = new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" });

export function PainelFiltros({ filtros, meses, marcas, cores, geradoEm, onChange }: Props) {
  const [aberto, setAberto] = useState(false);
  const id = useId();
  const selecionadas = filtros.marcas ?? marcas;

  const alternarMarca = (marca: string) => {
    const atual = new Set(selecionadas);
    if (atual.has(marca)) atual.delete(marca);
    else atual.add(marca);
    const lista = marcas.filter((m) => atual.has(m));
    onChange({ ...filtros, marcas: lista.length === marcas.length ? null : lista });
  };

  return (
    <aside className={`sidebar${aberto ? " aberta" : ""}`} aria-label="Filtros">
      <div className="sidebar-marca">
        <div className="logo" aria-hidden="true">DV</div>
        <div>
          <strong>Dash Vendas</strong>
          <span>Faturamento &amp; devoluções</span>
        </div>
        <button
          type="button"
          className="filtros-toggle"
          aria-expanded={aberto}
          aria-controls={`${id}-corpo`}
          onClick={() => setAberto((v) => !v)}
        >
          {aberto ? "Fechar filtros" : "Filtros"}
        </button>
      </div>

      <div className="filtros-corpo" id={`${id}-corpo`}>
        <fieldset className="grupo">
          <legend>Período</legend>
          <label className="campo">
            <span>Tipo de filtro</span>
            <select
              value={filtros.mes ? "mes" : "todos"}
              onChange={(e) =>
                onChange({ ...filtros, mes: e.target.value === "mes" ? meses[meses.length - 1] : null })
              }
            >
              <option value="mes">Por mês</option>
              <option value="todos">Todos os dados</option>
            </select>
          </label>
          {filtros.mes && (
            <label className="campo">
              <span>Mês</span>
              <select value={filtros.mes} onChange={(e) => onChange({ ...filtros, mes: e.target.value })}>
                {meses.map((mes) => (
                  <option key={mes} value={mes}>
                    {rotuloMes(mes)}
                  </option>
                ))}
              </select>
            </label>
          )}
        </fieldset>

        <fieldset className="grupo">
          <legend>Unidades</legend>
          <div className="opcoes">
            {marcas.map((marca) => (
              <label key={marca} className="opcao">
                <input
                  type="checkbox"
                  checked={selecionadas.includes(marca)}
                  onChange={() => alternarMarca(marca)}
                />
                <span className="cor" style={{ background: cores[marca] }} aria-hidden="true" />
                {marca.replace(/^UNIDADE /, "")}
              </label>
            ))}
          </div>
          <div className="acoes-marcas">
            <button
              type="button"
              className="botao-link"
              disabled={filtros.marcas === null}
              onClick={() => onChange({ ...filtros, marcas: null })}
            >
              Selecionar todas
            </button>
          </div>
        </fieldset>

        <fieldset className="grupo">
          <legend>Dia</legend>
          <label className="campo">
            <span>Dia do mês</span>
            <select
              value={filtros.dia ?? ""}
              onChange={(e) => onChange({ ...filtros, dia: e.target.value ? Number(e.target.value) : null })}
            >
              <option value="">Todos os dias</option>
              {Array.from({ length: 31 }, (_, i) => i + 1).map((dia) => (
                <option key={dia} value={dia}>
                  Dia {dia}
                </option>
              ))}
            </select>
          </label>
        </fieldset>

        <fieldset className="grupo">
          <legend>Receita</legend>
          <div className="opcoes" role="radiogroup" aria-label="Tipo de receita">
            {RECEITAS.map(({ valor, ajuda }) => (
              <label key={valor} className="opcao" title={ajuda}>
                <input
                  type="radio"
                  name={`${id}-receita`}
                  checked={filtros.receita === valor}
                  onChange={() => onChange({ ...filtros, receita: valor })}
                />
                {valor}
                <span className="sr-only"> ({ajuda})</span>
              </label>
            ))}
          </div>
        </fieldset>

        <p className="rodape-sidebar">Dados gerados em {dataGeracao.format(new Date(geradoEm))}</p>
      </div>
    </aside>
  );
}
