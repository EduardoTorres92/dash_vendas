# 📦 Sistema de Embarques Falsos

## 🎯 Objetivo

Gerar dados fictícios de embarques em aberto (potencial de faturamento) com **marcas já padronizadas** e dados completamente anonimizados.

## 📊 Dados Gerados

### Estrutura do Arquivo

O arquivo `embarques_falsos.xlsx` contém as seguintes colunas:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| `Estab` | Estabelecimento | `01`, `02`, `03` |
| `Unid. Negócio` | Marca padronizada | `MARCA A`, `MARCA B`, `MARCA C`, `MARCA D` |
| `Embarque` | Número do embarque | `123456` |
| `Dt Embarque` | Data do embarque | `2025-10-01` |
| `Status` | Status (vazio = potencial) | ` `, `FATURADO`, `CANCELADO` |
| `PARADOS` | Se está parado | ` `, `SIM` |
| `Nr Ped Cli` | Número pedido cliente | `ELC-45678` |
| `Vl Net` | Valor líquido | `15234.56` |
| `Situação` | Situação do embarque | `NaN`, `PENDENTE`, `EM SEPARAÇÃO` |
| `Desc Canal` | Canal de venda | `B2B ATACADO`, `B2B VAREJO`, etc. |
| `UF Cli` | Estado do cliente | `SP`, `RJ`, `MG`, etc. |

### Estatísticas dos Dados Gerados

**Embarques:**
- Total: 500 embarques
- Potenciais (Status vazio): ~70% (350 embarques)
- Faturados: ~20% (100 embarques)
- Cancelados: ~5% (25 embarques)

**Valores:**
- Total Geral: ~R$ 9,6 milhões
- Potencial: ~R$ 7,3 milhões
- Valor Médio: ~R$ 19.300

**Distribuição por Marca:**
- MARCA A: 40% dos embarques (maior volume)
- MARCA B: 30% dos embarques
- MARCA C: 20% dos embarques
- MARCA D: 10% dos embarques

**Canais de Venda:**
- B2B ATACADO: 25%
- B2B VAREJO: 30%
- B2B PROFISSIONAL: 20%
- B2C: 10%
- E-COMMERCE: 8%
- OEM: 5%
- NOVOS CANAIS: 2%

## 🚀 Como Usar

### 1️⃣ Gerar Embarques Falsos

```bash
python gerar_embarques_falsos.py
```

**O que acontece:**
- ✅ Gera 500 embarques fictícios
- ✅ Marcas já padronizadas (MARCA A, B, C, D)
- ✅ Canais já categorizados
- ✅ Pedidos já anonimizados
- ✅ Valores realistas
- ✅ Salva `embarques_falsos.xlsx`

### 2️⃣ Dashboard Carrega Automaticamente

O `ETL_embarques.py` detecta automaticamente:

```python
if existe 'embarques_falsos.xlsx':
    ⚡ Carrega dados falsos (já anonimizados)
else:
    📂 Carrega arquivo original
```

**Vantagens:**
- ✅ Sem necessidade de ter arquivo original
- ✅ Dados já processados e padronizados
- ✅ Carregamento rápido
- ✅ 100% anonimizado

## 📝 Personalização

### Alterar Quantidade de Embarques

Edite `gerar_embarques_falsos.py`:

```python
num_embarques = 500  # Altere para o número desejado
```

### Ajustar Distribuição por Marca

```python
marcas = ['MARCA A', 'MARCA B', 'MARCA C', 'MARCA D']
pesos_marcas = [0.4, 0.3, 0.2, 0.1]  # Altere os pesos
```

### Modificar Faixas de Valor

```python
if marca == 'MARCA A':
    valor_base = np.random.uniform(5000, 50000)  # Altere os valores
elif marca == 'MARCA B':
    valor_base = np.random.uniform(3000, 30000)
# ... e assim por diante
```

## 🔄 Fluxo de Dados

```
gerar_embarques_falsos.py
    ↓
embarques_falsos.xlsx (gerado)
    ↓
ETL_embarques.py (detecta automaticamente)
    ↓
Dashboard exibe potencial de faturamento ⚡
```

## 📊 Exemplo de Saída

```
================================================================================
GERANDO DADOS FALSOS DE EMBARQUES
================================================================================

📊 Gerando embarques...
✅ Embarques gerados: 500

📊 Estatísticas:
  - Embarques potenciais (Status vazio): 376
  - Embarques faturados: 100
  - Embarques cancelados: 24

💰 Valores:
  - Total geral: R$ 9,661,160.26
  - Potencial (Status vazio): R$ 7,345,128.07
  - Valor médio: R$ 19,322.32

🏷️  Distribuição por marca:
  - MARCA A: 217 embarques, R$ 5,878,307.12 (Potencial: R$ 4,524,603.16)
  - MARCA B: 148 embarques, R$ 2,438,888.68 (Potencial: R$ 1,789,270.08)
  - MARCA C: 84 embarques, R$ 951,866.91 (Potencial: R$ 735,703.40)
  - MARCA D: 51 embarques, R$ 392,097.55 (Potencial: R$ 295,551.43)
```

## 🎯 Benefícios

### Segurança
- ✅ **100% Anonimizado** - nenhum dado real
- ✅ **Marcas Padronizadas** - MARCA A, B, C, D
- ✅ **Pedidos Fictícios** - ELC-xxxxx, TEC-xxxxx
- ✅ **Valores Realistas** - mas totalmente fictícios

### Performance
- ⚡ **Geração Rápida** - 500 embarques em segundos
- ⚡ **Carregamento Rápido** - arquivo otimizado
- ⚡ **Pronto para Uso** - sem processamento adicional

### Flexibilidade
- 🔧 **Configurável** - ajuste quantidades e valores
- 🔧 **Reproduzível** - seed fixo garante mesmos dados
- 🔧 **Escalável** - gere quantos embarques quiser

## 🆘 Problemas?

**Erro ao carregar embarques:**
```bash
# Gere novamente o arquivo
python gerar_embarques_falsos.py
```

**Quer dados diferentes:**
```bash
# Edite a seed no script
Faker.seed(123)  # Use um número diferente
python gerar_embarques_falsos.py
```

**Valores muito altos/baixos:**
```bash
# Ajuste as faixas de valor no script
valor_base = np.random.uniform(MIN, MAX)
```

## 📁 Arquivos Relacionados

- `gerar_embarques_falsos.py` - Script gerador
- `embarques_falsos.xlsx` - Dados gerados
- `ETL_embarques.py` - Carrega os dados
- `faturamento.py` - Dashboard principal

---

**Dados 100% fictícios e seguros! 🔒**


