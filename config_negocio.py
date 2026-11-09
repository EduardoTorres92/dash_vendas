"""
Parâmetros de negócio do dashboard — EXEMPLO GENÉRICO.

Tudo o que é específico de uma empresa (nomes de arquivo, códigos de tipo de
operação, taxonomia de canais, depósitos, exclusões) fica aqui, fora do código
dos ETLs. Os valores abaixo são genéricos e combinam com os dados de
demonstração do repositório.

Para usar com os dados reais da sua empresa:
  1. copie este arquivo para `config_local.py` (ele está no .gitignore e nunca
     vai para o repositório);
  2. ajuste os valores para o seu ERP.
O `config_local.py` só precisa ter o que muda: o que não estiver lá vem daqui.
"""

# ---------------------------------------------------------------------------
# Arquivos
# ---------------------------------------------------------------------------
# Dados fictícios usados pelo botão "Usar dados de demonstração"
ARQUIVO_DEMO_FATURAMENTO = "dados_demo/faturamento_demo.csv"
ARQUIVO_DEMO_EMBARQUES = "dados_demo/embarques_demo.xlsx"

# Nomes esperados se os arquivos reais forem deixados na pasta do projeto
# (alternativa ao envio pela tela; nunca versionados por causa do .gitignore)
ARQUIVO_FATURAMENTO = "faturamento.csv"
ARQUIVO_EMBARQUES = "embarques.xlsx"

# Aba da planilha de embarques. None = usa a primeira aba que tiver as colunas esperadas.
ABA_EMBARQUES = None

# ---------------------------------------------------------------------------
# Relatório de faturamento
# ---------------------------------------------------------------------------
# Séries de nota fiscal consideradas
SERIES_NOTA_FISCAL = ["3", "12"]

# Depósitos considerados no faturamento e nas devoluções
DEPOSITOS_FATURAMENTO = ["CD01", "CD02", "CD03", "DEV01", "CD04", "CD05", "N/A", "MKT01"]
DEPOSITOS_DEVOLUCAO = ["CD01", "CD02", "CD03", "DEV01", "CD04", "CD05"]

# Marcas/unidades e itens que não entram nas análises
MARCAS_EXCLUIDAS = ["?"]
ITENS_EXCLUIDOS = []  # valores de "Desc Item" (ex.: itens de serviço ou consumo interno)

# Valor de "Localização" que marca vendas para o exterior (fora das devoluções)
LOCALIZACAO_EXPORTACAO = "EXPORTAÇÃO"

# Tipo de operação do ERP -> categoria usada no painel.
# Só as operações listadas aqui entram no faturamento.
TIPOS_OPERACAO_FATURAMENTO = {
    "1 - Venda": "RECEITA DIRETA",
    "2 - Revenda": "RECEITA REVENDA",
    "3 - Bonificação": "BONIFICAÇÃO",
    "4 - Transferência": "TRANSFERÊNCIA",
}
# Operações de devolução (todas viram a categoria "DEVOLUÇÃO")
TIPOS_OPERACAO_DEVOLUCAO = ["5 - Devolução de venda", "6 - Devolução de compra"]

# Canal do cadastro do cliente -> grupo de canal exibido no painel.
# Valores que não aparecem aqui ficam como estão.
MAPEAMENTO_CANAIS = {
    "ATACADISTA": "B2B ATACADO",
    "DISTRIBUIDOR": "B2B ATACADO",
    "SUPERMERCADO": "B2B VAREJO",
    "LOJA DE VAREJO": "B2B VAREJO",
    "REVENDA TECNICA": "B2B PROFISSIONAL",
    "INSTALADOR": "B2B PROFISSIONAL",
    "CONSUMIDOR FINAL": "B2C",
    "LOJA VIRTUAL": "E-COMMERCE",
    "VENDA DIRETA": "OEM",
    "INTERCOMPANY": "VENDA INTERNA",
    "NOVOS CANAIS": "NOVOS CANAIS",
}

# ---------------------------------------------------------------------------
# Planilha de embarques (potencial de faturamento)
# ---------------------------------------------------------------------------
# Valores de "Unid. Negócio" que devem ser ignorados (ex.: linhas de total ou de teste)
UNIDADES_EMBARQUE_EXCLUIDAS = []
