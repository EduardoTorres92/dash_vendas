import { useEffect, useMemo, useState } from "react";
import { CardMarca } from "./components/CardMarca";
import { PainelFiltros } from "./components/PainelFiltros";
import { calcularCards, rotuloMes } from "./lib/regras";
import type { DadosFaturamento, Filtros } from "./lib/tipos";
import { gravarFiltrosNaUrl, lerFiltrosDaUrl } from "./lib/url";

type Estado =
  | { tipo: "carregando" }
  | { tipo: "erro"; mensagem: string }
  | { tipo: "pronto"; dados: DadosFaturamento };

const COR_PADRAO = "#64748b";

export function App() {
  const [estado, setEstado] = useState<Estado>({ tipo: "carregando" });

  useEffect(() => {
    let ativo = true;
    fetch("/data/faturamento.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<DadosFaturamento>;
      })
      .then((dados) => ativo && setEstado({ tipo: "pronto", dados }))
      .catch((e: unknown) =>
        ativo && setEstado({ tipo: "erro", mensagem: e instanceof Error ? e.message : String(e) }),
      );
    return () => {
      ativo = false;
    };
  }, []);

  if (estado.tipo === "pronto") return <Painel dados={estado.dados} />;

  return (
    <div className="app">
      <aside className="sidebar" aria-hidden="true" />
      <main className="principal">
        <Cabecalho chips={[]} />
        {estado.tipo === "erro" ? (
          <p className="estado erro" role="alert">
            Não foi possível carregar os dados ({estado.mensagem}). Recarregue a página para tentar de novo.
          </p>
        ) : (
          <div className="grade-cards" aria-busy="true" aria-label="Carregando dados">
            {Array.from({ length: 6 }, (_, i) => (
              <div key={i} className="esqueleto" />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function Painel({ dados }: { dados: DadosFaturamento }) {
  const mesPadrao = dados.meses[dados.meses.length - 1];
  const [filtros, setFiltros] = useState<Filtros>(() =>
    lerFiltrosDaUrl({ mes: mesPadrao, marcas: null, dia: null, receita: "Ambas" }, dados.meses, dados.marcas),
  );

  useEffect(() => gravarFiltrosNaUrl(filtros, mesPadrao), [filtros, mesPadrao]);

  const cards = useMemo(() => calcularCards(dados, filtros), [dados, filtros]);

  const marcasSelecionadas = filtros.marcas ?? dados.marcas;
  const titulo =
    marcasSelecionadas.length === dados.marcas.length
      ? "Faturamento líquido por marca"
      : `Faturamento líquido por marca - ${marcasSelecionadas.join(", ")}`;

  let periodo = filtros.mes ? rotuloMes(filtros.mes) : "Todo o histórico";
  if (filtros.dia) periodo += ` · Dia ${filtros.dia}`;

  return (
    <div className="app">
      <PainelFiltros
        filtros={filtros}
        meses={dados.meses}
        marcas={dados.marcas}
        cores={dados.cores}
        geradoEm={dados.geradoEm}
        onChange={setFiltros}
      />
      <main className="principal">
        <Cabecalho
          chips={[
            ["Período", periodo],
            [
              "Unidades",
              marcasSelecionadas.length === dados.marcas.length
                ? "Todas"
                : `${marcasSelecionadas.length} de ${dados.marcas.length}`,
            ],
            ["Receita", filtros.receita],
          ]}
        />

        <section aria-labelledby="titulo-liquido">
          <div className="secao">
            <h2 id="titulo-liquido">{titulo}</h2>
            <p>Líquido = bruto + cut-off inicial − cut-off − devoluções. Variação comparada ao mês anterior.</p>
          </div>

          {marcasSelecionadas.length === 0 ? (
            <p className="estado">Selecione ao menos uma unidade nos filtros.</p>
          ) : cards.length === 0 ? (
            <p className="estado">Nenhum faturamento encontrado para os filtros selecionados.</p>
          ) : (
            <ul className="grade-cards" aria-live="polite">
              {cards.map((card) => (
                <CardMarca
                  key={card.marca}
                  card={card}
                  cor={dados.cores[card.marca.toUpperCase()] ?? COR_PADRAO}
                  semComparacao={!filtros.mes}
                />
              ))}
            </ul>
          )}
        </section>

        <p className="nota">
          Versão web em construção: esta página traz a seção principal do dashboard. As demais seções seguem
          disponíveis na versão Streamlit.
        </p>
      </main>
    </div>
  );
}

function Cabecalho({ chips }: { chips: [string, string][] }) {
  return (
    <header className="cabecalho">
      <div>
        <p className="eyebrow">Painel comercial</p>
        <h1>Faturamento</h1>
        <p className="sub">Faturamento líquido, devoluções e cut-off por unidade de negócio.</p>
      </div>
      {chips.length > 0 && (
        <ul className="chips" aria-label="Filtros ativos">
          {chips.map(([rotulo, valor]) => (
            <li key={rotulo} className="chip">
              {rotulo} <b>{valor}</b>
            </li>
          ))}
        </ul>
      )}
    </header>
  );
}
