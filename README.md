# 📊 Dashboard de Análise de Faturamento

Dashboard interativo desenvolvido em Python com Streamlit para análise completa de faturamento, devoluções e potencial de embarques. Sistema completo com ETL automatizado, anonimização de dados sensíveis e visualizações dinâmicas.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-green.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.17+-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Visão Geral

Este projeto oferece uma solução completa para análise de dados de faturamento com recursos avançados de visualização e processamento de dados. Ideal para equipes comerciais, financeiras e de gestão que precisam tomar decisões baseadas em dados.

## ✨ Funcionalidades Principais

### 📈 Análises de Faturamento
- **Visão Geral**: Métricas principais (faturamento bruto, líquido, devoluções)
- **Análise Temporal**: Evolução mensal e comparativos período a período
- **Análise por Unidade de Negócio**: Performance detalhada por marca/unidade
- **Análise por Canal**: Distribuição por canais de venda (B2B, B2C, E-commerce, etc.)
- **Análise Regional**: Faturamento por estado com mapa interativo do Brasil em 2D e 3D (MapLibre, funciona sem internet)
- **Top Produtos**: Ranking dos produtos mais vendidos
- **Top Clientes**: Ranking de clientes por faturamento

### 📦 Análise de Embarques
- **Potencial de Faturamento**: Análise de embarques pendentes
- **Embarques por Unidade**: Visualização do pipeline de vendas
- **Análise por Canal**: Distribuição de embarques por canal de venda
- **Identificação de Oportunidades**: Embarques prontos para faturamento

### 🔄 Sistema ETL Automatizado
- **Processamento Otimizado**: ETL completo para dados de faturamento, devoluções e embarques
- **Anonimização Segura**: Proteção de dados sensíveis com hash MD5
- **Cache Inteligente**: Sistema de cache para melhor performance
- **Carregamento Rápido**: Processamento prévio para inicialização em segundos

### 🔒 Segurança e Privacidade
- ✅ Nomes de clientes anonimizados com consistência
- ✅ Códigos de produtos fictícios
- ✅ Números de pedidos mascarados
- ✅ Valores mantidos proporcionais aos originais
- ✅ Impossível reverter para dados originais

## 🎨 Design System

O layout segue a direção visual gerada com a skill **UI/UX Pro Max** para o tipo de produto *Analytics/Financial Dashboard*:

- **Estilo**: Data-Dense Dashboard + Minimal Swiss — cards compactos, grade enxuta, foco nos números.
- **Paleta**: azul de dados `#1E40AF`, destaque âmbar `#D97706`, fundo `#F8FAFC`, positivo `#059669`, negativo `#DC2626`.
- **Tipografia**: Fira Sans (texto) + Fira Code (valores, com algarismos tabulares).
- **Acessibilidade**: contraste ≥ 4.5:1, variações com seta e sinal (não só cor), sem emojis como ícones, `prefers-reduced-motion` respeitado.

Tokens, CSS global, template Plotly (`dash_vendas`) e componentes (cabeçalho, seções, cards de KPI e de meta) ficam em `ui_theme.py`; o tema base do Streamlit está em `.streamlit/config.toml`.

## 🏢 Uso Local na Empresa (dados reais)

O painel roda **só no seu computador**: o Streamlit aceita conexões apenas de `127.0.0.1`, não envia estatísticas de uso e os arquivos são processados em memória, sem serem gravados em disco nem enviados para fora.

1. **Sincronize o repositório** (só código; os dados não ficam no Git):
   ```bash
   git clone https://github.com/EduardoTorres92/dash_vendas.git   # primeira vez
   git pull                                                       # nas próximas
   ```
2. **Abra o painel**: dê dois cliques em `iniciar.bat` (Windows) ou rode `./iniciar.sh` (macOS/Linux). Na primeira vez ele cria o ambiente Python (`.venv`) e instala as dependências; depois abre `http://localhost:8501`.
3. **Carregue os dados pela tela inicial**:
   - **Relatório de faturamento** (`.csv` separado por `;`) — obrigatório;
   - **Planilha de embarques** (`.xlsx`) — opcional, usada no Potencial x Faturamento.
4. Para usar outro arquivo, clique em **Trocar dados** na barra lateral.

**Configuração do seu ERP:** códigos de tipo de operação, canais, depósitos e séries ficam em `config_local.py` (fora do Git), a partir do exemplo `config_negocio.py`. Veja [README_DADOS.md](README_DADOS.md).

Com arquivos enviados, os dados aparecem **como estão** (sem anonimização). O botão **Usar dados de demonstração** abre o painel com os dados fictícios do repositório, útil para desenvolver sem acesso aos dados reais.

> 🔒 O `.gitignore` bloqueia `*.csv`, `*.xlsx` e `*.xls` (exceto os dois arquivos de demonstração), para que um relatório real nunca seja enviado ao GitHub por engano.

Requisitos: Python 3.10+ (na instalação do Windows, marque *Add python.exe to PATH*). Se a rede da empresa usa proxy, configure-o no pip antes da primeira execução.

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonar o repositório)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/EduardoTorres92/dash_vendas.git
cd dash_vendas
```

2. **Crie um ambiente virtual (recomendado)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute o dashboard**
```bash
streamlit run faturamento.py
```

O dashboard abre no navegador em `http://localhost:8501`, na tela de carregamento: envie o relatório de faturamento (e, se quiser, a planilha de embarques) ou use os dados de demonstração. Veja [Uso Local na Empresa](#-uso-local-na-empresa-dados-reais).

## 📁 Estrutura do Projeto

```
Projeto Dash/
├── faturamento.py              # Dashboard principal (Streamlit)
├── fonte_dados.py              # Tela de carregamento dos arquivos (upload) e modo demonstração
├── config_negocio.py           # Parâmetros de negócio (exemplo genérico)
├── configuracao.py             # Junta config_negocio.py e o config_local.py (fora do Git)
├── dados_demo/                 # Dados fictícios de demonstração
├── iniciar.bat / iniciar.sh    # Inicializadores do painel local
├── ui_theme.py                 # Design system (tokens, CSS, template Plotly, componentes)
├── .streamlit/config.toml      # Tema base do Streamlit
├── ETL_faturamento.py          # ETL de dados de faturamento
├── ETL_devolucao.py            # ETL de devoluções
├── ETL_embarques.py            # ETL de embarques
├── cut_off_mensal.py           # Valores de cut-off por mês
├── conversoes.py               # Leitura de datas e números do ERP (formato brasileiro)
├── mapa_estados.py             # Mapa por estado (componente Streamlit com MapLibre)
├── static/                     # MapLibre GL JS e malha dos estados, servidos localmente
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
└── README_DADOS.md             # Fontes de dados, configuração e formato dos arquivos
```

## 📊 Visualizações Disponíveis

### Gráficos Interativos
- 📊 **Gráficos de Barras**: Comparação de valores entre categorias
- 📈 **Gráficos de Linha**: Evolução temporal de métricas
- 🗺️ **Mapa por estado em 2D e 3D**: zoom, giro e inclinação, dica ao passar o mouse e clique para fixar um estado. O MapLibre e a malha dos estados (IBGE, simplificada) ficam em `static/` e são servidos pelo próprio Streamlit (`enableStaticServing`), então o mapa funciona sem internet e os dados não saem do computador
- 🥧 **Gráficos de Pizza**: Participação percentual
- 📋 **Tabelas Dinâmicas**: Dados detalhados com ordenação e filtros

### Cards de Métricas
- Faturamento bruto e líquido
- Quantidade de notas fiscais
- Ticket médio
- Taxa de devolução
- Potencial de embarques

## 🔧 Configuração de Dados

Formato dos arquivos, colunas usadas e parâmetros de configuração: veja [README_DADOS.md](README_DADOS.md).

## ⚙️ Personalização

### Modificar Unidades de Negócio
Edite o arquivo `ETL_faturamento.py` para ajustar o mapeamento de marcas/unidades.

### Ajustar Canais de Venda
Modifique o dicionário `mapeamento_canais` em `ETL_faturamento.py` para categorizar seus canais específicos.

### Configurar Cut-off Mensal
Edite `cut_off_mensal.py` para definir valores de cut-off por mês e unidade.

## 📈 Performance

### Otimizações Implementadas
- ✅ Cache inteligente de dados anonimizados
- ✅ Processamento prévio de transformações
- ✅ Carregamento lazy de dados
- ✅ Uso eficiente de memória com pandas

### Benchmark
- **Antes**: 2-5 minutos para carregar
- **Depois**: 5-10 segundos para carregar
- **Otimização**: 10-20x mais rápido! ⚡

## 🛡️ Anonimização de Dados

O sistema utiliza hash MD5 para garantir:
1. **Consistência**: O mesmo dado original sempre gera o mesmo dado falso
2. **Segurança**: Impossível reverter dados anonimizados para originais
3. **Realismo**: Dados falsos mantêm formato e proporções realistas
4. **Cache Persistente**: Anonimização consistente entre execuções

## 🎨 Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)**: Framework para criação do dashboard web
- **[Pandas](https://pandas.pydata.org/)**: Manipulação e análise de dados
- **[Plotly](https://plotly.com/)**: Visualizações interativas
- **[Faker](https://faker.readthedocs.io/)**: Geração de dados falsos
- **[NumPy](https://numpy.org/)**: Operações numéricas
- **[openpyxl](https://openpyxl.readthedocs.io/)**: Leitura de arquivos Excel

## 📝 Documentação Adicional

- 📘 [README_DADOS.md](README_DADOS.md) - Fontes de dados, configuração do ERP e formato dos arquivos

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### Diretrizes de Contribuição
- Mantenha o código limpo e documentado
- Adicione testes quando aplicável
- Atualize a documentação conforme necessário
- Siga as boas práticas de Python (PEP 8)

## 🐛 Problemas Comuns e Soluções

### O painel não encontra registros no arquivo enviado
Confira se as séries, depósitos e tipos de operação em `config_local.py` correspondem aos do seu ERP (veja [README_DADOS.md](README_DADOS.md)).

### Erro de módulo não encontrado
```bash
# Reinstale as dependências
pip install -r requirements.txt
```

### Dados parecem incorretos
```bash
# Delete o cache e recarregue
del .cache_anonimizacao.pkl
streamlit run faturamento.py
```

### Performance lenta
O primeiro carregamento de um arquivo grande leva alguns segundos; depois os resultados ficam em cache enquanto o mesmo arquivo estiver carregado.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autor

**Eduardo Torres**

- GitHub: [@EduardoTorres92](https://github.com/EduardoTorres92)

## 🌟 Agradecimentos

- Equipe que contribuiu com feedbacks e melhorias
- Comunidade Streamlit pelos excelentes recursos
- Todos que utilizam e apoiam este projeto

## 📊 Estatísticas do Projeto

- ⭐ Stars: 0
- 🔀 Forks: 0
- 📝 Commits: 10+
- 🐛 Issues: 0

---

**Desenvolvido com ❤️ usando Python e Streamlit**

Se este projeto foi útil para você, considere dar uma ⭐!

