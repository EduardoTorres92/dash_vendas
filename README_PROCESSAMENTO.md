# 📊 Processamento de Dados - Dashboard Faturamento

## 🚀 Como Funciona

Este projeto usa um sistema de **processamento otimizado** para carregar dados muito mais rápido!

### Fluxo de Dados

```
ESFT0100.csv (original)
    ↓
[processar_dados_inicial.py]
    ↓
ESFT0100_processado.csv (anonimizado + transformado)
    ↓
[faturamento.py] → Dashboard carrega RÁPIDO! ⚡
```

## 📝 Instruções

### 1️⃣ Primeira Vez / Novos Dados

Quando você tiver dados novos ou for usar pela primeira vez:

```bash
python processar_dados_inicial.py
```

**O que este script faz:**
- ✅ Carrega `ESFT0100.csv`
- ✅ Anonimiza todos os dados sensíveis:
  - **Item** → códigos como `ELET-8833-874`
  - **Desc Item** → descrições como `Scanner Premium Compacto`
  - **Razao Social** → nomes fictícios como `TechMax Eletrônicos LTDA`
  - **Ped Cliente** → códigos como `ELC-45678`
  - **Vl Net Livro** → valores realistas gerados (R$ 10 a R$ 15.000)
- ✅ Aplica todas as transformações e categorizações
- ✅ Padroniza marcas (MARCA A, B, C, etc.)
- ✅ Salva `ESFT0100_processado.csv`
- ✅ Cria cache persistente `.cache_anonimizacao.pkl`

**Tempo:** ~30-60 segundos (só precisa fazer UMA VEZ!)

### 2️⃣ Executar o Dashboard

Depois de processar os dados:

```bash
streamlit run faturamento.py
```

**O que acontece:**
- ⚡ O dashboard detecta automaticamente o arquivo processado
- ⚡ Carrega os dados em **segundos** (ao invés de minutos!)
- ⚡ Todas as anonimizações já estão aplicadas
- ⚡ Todas as transformações já estão feitas

## 🔄 Quando Reprocessar?

Execute `processar_dados_inicial.py` novamente quando:

- 📥 Houver novos dados em `ESFT0100.csv`
- 🔄 Quiser gerar novos valores falsos (delete `.cache_anonimizacao.pkl` antes)
- 🐛 Houver problemas com os dados processados

## 📁 Arquivos do Sistema

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| `ESFT0100.csv` | Dados originais | Atualizar com novos dados |
| `processar_dados_inicial.py` | Script de processamento | Executar quando tiver novos dados |
| `ESFT0100_processado.csv` | Dados prontos para uso | Gerado automaticamente |
| `.cache_anonimizacao.pkl` | Cache de anonimização | Gerado automaticamente |
| `faturamento.py` | Dashboard principal | Executar para ver relatórios |

## ⚡ Benefícios

### Antes (processamento em tempo real):
- ⏱️ Carregamento: **2-5 minutos**
- 💻 Processamento a cada execução
- 🐌 Interface lenta

### Depois (processamento prévio):
- ⚡ Carregamento: **5-10 segundos**
- 💾 Processamento uma única vez
- 🚀 Interface rápida

## 🔒 Segurança dos Dados

Todos os dados sensíveis são anonimizados de forma **consistente**:

- ✅ **Mesmo item** → mesmo preço unitário (consistente)
- ✅ **Hash MD5** garante consistência de todos os dados
- ✅ **Valores realistas**: preços entre R$ 10 e R$ 15.000
- ✅ **Cálculo automático**: Valor Total = Preço Unitário × Quantidade
- ✅ Cache compartilhado entre todas as funções
- ✅ Impossível reverter para dados originais

## 💡 Dicas

1. **Git:** Adicione ao `.gitignore`:
   ```
   ESFT0100.csv
   ESFT0100_processado.csv
   .cache_anonimizacao.pkl
   ```

2. **Backup:** Sempre mantenha backup do `ESFT0100.csv` original

3. **Performance:** O arquivo processado é **10-20x mais rápido** para carregar!

4. **Cache:** O cache `.pkl` garante que mesmos valores sempre geram mesmos dados falsos

## 🆘 Problemas?

**Dashboard não carrega dados:**
```bash
# Execute o processamento primeiro
python processar_dados_inicial.py
```

**Dados parecem errados:**
```bash
# Delete o cache e reprocesse
del .cache_anonimizacao.pkl
python processar_dados_inicial.py
```

**Quer dados falsos diferentes:**
```bash
# Delete o cache para gerar novos valores
del .cache_anonimizacao.pkl
del ESFT0100_processado.csv
python processar_dados_inicial.py
```

## 📊 Estrutura do Projeto

```
Projeto Dash/
├── ESFT0100.csv                    # Dados originais
├── processar_dados_inicial.py      # Script de processamento
├── ESFT0100_processado.csv         # Dados processados (gerado)
├── .cache_anonimizacao.pkl         # Cache (gerado)
├── faturamento.py                  # Dashboard principal
├── ETL_faturamento.py              # Funções ETL
├── ETL_devolucao.py                # ETL devoluções
├── ETL_embarques.py                # ETL embarques
└── README_PROCESSAMENTO.md         # Este arquivo
```

---

**Desenvolvido para máxima performance! 🚀**

