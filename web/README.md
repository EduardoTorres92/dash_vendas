# Dash Vendas — versão web

Versão estática do dashboard de faturamento, feita para publicar na Netlify.
Usa **Vite + React + TypeScript** e o mesmo design system da versão Streamlit
(`ui_theme.py`).

> **Status:** primeira etapa da migração. Esta versão traz a seção
> **Faturamento líquido por marca** com os filtros de período, unidades, dia e
> tipo de receita. As demais seções continuam no Streamlit (`faturamento.py`).

## Como funciona

As regras de negócio continuam no Python:

```
ESFT0100_processado.csv ──► scripts/exportar_dados.py ──► web/public/data/faturamento.json ──► React
   (dados)                  (mesmos ETLs do Streamlit)     (NFs consolidadas, cut-offs,     (filtra e soma)
                                                             totais do mês anterior)
```

- O exportador usa as funções de `ETL_faturamento.py` e `ETL_devolucao.py`.
- O frontend só aplica os filtros e a fórmula do líquido
  (`src/lib/regras.ts`):
  **líquido = bruto + cut-off inicial − cut-off − devoluções**.
- O **teste de paridade** (`tests/paridade.test.ts`) compara o resultado do
  frontend com o calculado pelo Python, seguindo o `faturamento.py` passo a
  passo, em 38 combinações de filtros. No build da Netlify, se os números
  divergirem, o deploy falha.

## Rodando localmente

Requisitos: Node 22.12+ e Python 3.10+ com `pip install -r ../scripts/requirements.txt`.

```bash
cd web
npm install
npm run dados:paridade   # gera public/data/faturamento.json e os casos de teste
npm test                 # teste de paridade com o Python
npm run dev              # http://localhost:5173
```

## Publicando na Netlify

A configuração está em [`../netlify.toml`](../netlify.toml) (base `web`,
publish `dist`). Para conectar:

1. Na Netlify, **Add new project → Import an existing project** e escolha este repositório.
2. Os campos de build vêm do `netlify.toml`; não é preciso preencher nada.
3. A cada push na branch de produção, a Netlify roda o exportador, o teste de
   paridade e o build.

Para atualizar os dados, substitua o `ESFT0100_processado.csv` e faça push.

> **Atenção:** o site é estático e o JSON de dados fica público para quem tem
> o link. Os dados deste repositório são anonimizados; com dados reais, ative
> proteção por senha na Netlify ou adicione autenticação.

## Filtros na URL

Os filtros ficam na query string, então dá para compartilhar uma visão:
`/?mes=2025-06&marcas=UNIDADE%20SOROCABA,UNIDADE%20CURITIBA&dia=3&receita=Sim`
(`mes=todos` para todo o histórico).
