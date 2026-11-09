# Dados e configuração

Como os dados entram no painel e como adaptá-lo ao ERP de uma empresa.

## Fontes de dados

| Modo | De onde vêm os dados | Anonimização |
|---|---|---|
| **Arquivos enviados pela tela** (uso real) | Relatório de faturamento (`.csv`) e, opcionalmente, planilha de embarques (`.xlsx`), enviados na tela inicial. Ficam só na memória. | Não: os dados aparecem como estão |
| **Demonstração** | `dados_demo/faturamento_demo.csv` e `dados_demo/embarques_demo.xlsx` (fictícios, versionados) | Já são fictícios |
| **Arquivos na pasta** (alternativa) | Relatórios reais com os nomes definidos em `ARQUIVO_FATURAMENTO` / `ARQUIVO_EMBARQUES`, deixados na pasta do projeto | Sim (itens, clientes e pedidos) |

O `.gitignore` bloqueia `*.csv`, `*.xlsx` e `*.xls`, exceto os dois arquivos de demonstração: relatórios reais nunca vão para o repositório.

## Configuração de negócio

Tudo o que depende da empresa — nomes de arquivo, séries de nota fiscal, depósitos, códigos de tipo de operação, taxonomia de canais e exclusões — fica fora do código dos ETLs:

- **`config_negocio.py`**: exemplo genérico, versionado. Combina com os dados de demonstração.
- **`config_local.py`**: valores reais do seu ERP. Fica só no computador onde o painel roda (está no `.gitignore`) e sobrepõe os valores do exemplo. Só precisa conter o que muda.
- **`configuracao.py`**: junta os dois; é o que os ETLs importam.

Para configurar: copie `config_negocio.py` para `config_local.py` e ajuste. Principais parâmetros:

| Parâmetro | Para que serve |
|---|---|
| `SERIES_NOTA_FISCAL` | Séries de NF consideradas no faturamento |
| `DEPOSITOS_FATURAMENTO` / `DEPOSITOS_DEVOLUCAO` | Depósitos considerados |
| `TIPOS_OPERACAO_FATURAMENTO` | Código do ERP → categoria (`RECEITA DIRETA`, `RECEITA REVENDA`, `BONIFICAÇÃO`, `TRANSFERÊNCIA`). Só essas operações entram no faturamento |
| `TIPOS_OPERACAO_DEVOLUCAO` | Códigos que contam como devolução |
| `MAPEAMENTO_CANAIS` | Canal do cadastro do cliente → grupo exibido no painel |
| `MARCAS_EXCLUIDAS` / `ITENS_EXCLUIDOS` | Marcas e itens fora das análises |
| `ABA_EMBARQUES` | Aba da planilha de embarques (`None` = detecta pela presença das colunas) |
| `UNIDADES_EMBARQUE_EXCLUIDAS` | Linhas a ignorar na planilha de embarques |

> As categorias de tipo de operação (`RECEITA DIRETA` etc.) são usadas pelo filtro "Tipo de receita" do painel: *Sim* = receita direta e revenda; *Não* = bonificação e transferência.

## Relatório de faturamento

CSV exportado do ERP, colunas separadas por `;`, codificação latin1 (ANSI), uma linha por item de nota fiscal. A tela de carregamento confere o formato e lista as colunas que faltarem.

Colunas usadas: `Marca`, `Deposito`, `Razao Social`, `Estado`, `Ped Cliente`, `Receita`, `Situacao Ped`, `Tipo Oper`, `Serie`, `Nota Fiscal`, `Dt Emis NF` (dd/mm/aa), `Dt Embarque` (dd/mm/aa), `Item`, `Desc Item`, `Localização`, `Quantidade`, `Vl Net Livro` (vírgula decimal), `Nro Embarque`, `Canal Venda Cliente`.

## Planilha de embarques

Usada na análise **Potencial x Faturamento**. A aba é encontrada automaticamente (a primeira com todas as colunas abaixo) ou definida em `ABA_EMBARQUES`.

Colunas usadas: `Estab`, `Unid. Negócio`, `Embarque`, `Dt Embarque`, `Status`, `PARADOS`, `Nr Ped Cli`, `Vl Net`, `Situação`, `Desc Canal`, `UF Cli`.

## Fluxo de processamento

```
Relatório (.csv) ─► fonte_dados.ler_relatorio_faturamento  (valida formato e colunas)
                 ─► ETL_faturamento / ETL_devolucao         (séries, depósitos, tipos de operação,
                                                             canais, exclusões — via configuracao.py)
                 ─► faturamento.py                          (filtros da barra lateral e visualizações)

Planilha (.xlsx) ─► ETL_embarques                          (potencial de faturamento por unidade)
```

Os resultados ficam em cache (memória) enquanto o mesmo arquivo estiver carregado; **Trocar dados** limpa o cache.
