/**
 * Garante que a versão web chega nos mesmos números do Streamlit.
 * Requer os arquivos gerados por: npm run dados:paridade
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { calcularCards } from "../src/lib/regras";
import type { CardMarca, DadosFaturamento, Filtros } from "../src/lib/tipos";

const ler = <T>(caminho: string): T =>
  JSON.parse(readFileSync(fileURLToPath(new URL(caminho, import.meta.url)), "utf-8")) as T;

const dados = ler<DadosFaturamento>("../public/data/faturamento.json");
const casos = ler<{ filtros: Filtros; cards: CardMarca[] }[]>("./fixtures/paridade.json");

const CENTAVO = 0.005;
const CAMPOS_VALOR = ["bruto", "devolucoes", "cutOff", "cutOffInicial", "liquido"] as const;

describe("paridade com o faturamento.py", () => {
  it("tem casos gerados", () => {
    expect(casos.length).toBeGreaterThan(10);
  });

  for (const { filtros, cards: esperados } of casos) {
    const nome = `mes=${filtros.mes ?? "todos"} marcas=${filtros.marcas?.length ?? "todas"} dia=${filtros.dia ?? "-"} receita=${filtros.receita}`;

    it(nome, () => {
      const obtidos = calcularCards(dados, filtros);
      expect(obtidos.map((c) => c.marca)).toEqual(esperados.map((c) => c.marca));

      esperados.forEach((esperado, i) => {
        const obtido = obtidos[i];
        for (const campo of CAMPOS_VALOR) {
          expect(Math.abs(obtido[campo] - esperado[campo]), `${esperado.marca}.${campo}`).toBeLessThan(CENTAVO);
        }
        expect(obtido.variacao, `${esperado.marca}.variacao`).toBeCloseTo(esperado.variacao, 6);
        expect(obtido.participacao, `${esperado.marca}.participacao`).toBeCloseTo(esperado.participacao, 6);
      });
    });
  }
});
