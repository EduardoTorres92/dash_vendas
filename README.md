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
- **Análise Regional**: Faturamento por estado com mapa interativo do Brasil
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

4. **Prepare seus dados**
   - Coloque seu arquivo de faturamento como `ESFT0100.csv` na raiz do projeto
   - Coloque seu arquivo de embarques como `embarques_falsos.xlsx` (ou configure o nome no código)

5. **Execute o dashboard**
```bash
streamlit run faturamento.py
```

O dashboard será aberto automaticamente no seu navegador em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
Projeto Dash/
├── faturamento.py              # Dashboard principal (Streamlit)
├── ui_theme.py                 # Design system (tokens, CSS, template Plotly, componentes)
├── .streamlit/config.toml      # Tema base do Streamlit
├── ETL_faturamento.py          # ETL de dados de faturamento
├── ETL_devolucao.py            # ETL de devoluções
├── ETL_embarques.py            # ETL de embarques
├── cut_off_mensal.py           # Valores de cut-off por mês
├── br_states.json              # Coordenadas dos estados brasileiros
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
├── README_EMBARQUES.md         # Documentação de embarques
└── README_PROCESSAMENTO.md     # Documentação do ETL
```

## 📊 Visualizações Disponíveis

### Gráficos Interativos
- 📊 **Gráficos de Barras**: Comparação de valores entre categorias
- 📈 **Gráficos de Linha**: Evolução temporal de métricas
- 🗺️ **Mapas Coropléticos**: Distribuição geográfica por estado
- 🥧 **Gráficos de Pizza**: Participação percentual
- 📋 **Tabelas Dinâmicas**: Dados detalhados com ordenação e filtros

### Cards de Métricas
- Faturamento bruto e líquido
- Quantidade de notas fiscais
- Ticket médio
- Taxa de devolução
- Potencial de embarques

## 🔧 Configuração de Dados

### Estrutura Esperada do Arquivo de Faturamento (ESFT0100.csv)

O arquivo CSV deve conter as seguintes colunas principais:
- `Marca`: Unidade de negócio
- `Dt Emis NF`: Data de emissão da nota fiscal
- `Item`: Código do produto
- `Desc Item`: Descrição do produto
- `Razao Social`: Nome do cliente
- `Ped Cliente`: Número do pedido
- `Vl Net Livro`: Valor líquido
- `Canal Venda Cliente`: Canal de venda
- `Estado`: UF do cliente
- `Nota Fiscal`: Número da nota fiscal

### Estrutura Esperada do Arquivo de Embarques

Consulte `README_EMBARQUES.md` para detalhes completos.

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

- 📘 [README_PROCESSAMENTO.md](README_PROCESSAMENTO.md) - Guia completo do sistema ETL
- 📗 [README_EMBARQUES.md](README_EMBARQUES.md) - Sistema de análise de embarques

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

### Dashboard não carrega dados
```bash
# Verifique se o arquivo de dados existe
ls ESFT0100.csv

# Se não existir, coloque seu arquivo de dados na raiz do projeto
```

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
```bash
# Verifique se está usando o arquivo processado
# O arquivo ESFT0100_processado.csv deve existir para melhor performance
```

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

