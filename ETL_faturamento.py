"""
ETL para dados de Faturamento
=============================

Este módulo contém todas as funções de ETL (Extract, Transform, Load) 
para processamento de dados de faturamento.

Autor: Sistema de Relatórios CI
Data: 2025
"""

import pandas as pd
import os
import sys
from faker import Faker
import hashlib
import pickle

import configuracao as cfg
from conversoes import para_data, para_numero

# Adicionar o diretório atual ao path para importar as funções de cut-off
current_dir = os.path.dirname(os.path.abspath(__file__))
# O arquivo cut_off_mensal.py agora está na raiz do projeto
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from cut_off_mensal import get_cut_off_mensal, get_cut_off_total_mensal
except ImportError as e:
    print(f"Erro ao importar cut_off_mensal: {e}")
    # Fallback: definir funções vazias
    def get_cut_off_mensal(mes, marca):
        return 0
    def get_cut_off_total_mensal(mes):
        return 0

# Inicializar Faker e dicionários de cache globais
_faker = Faker('pt_BR')

# Arquivo de cache persistente
_cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache_anonimizacao.pkl')

# Tentar carregar cache existente
def _carregar_cache():
    """Carrega cache persistente do disco"""
    if os.path.exists(_cache_file):
        try:
            with open(_cache_file, 'rb') as f:
                return pickle.load(f)
        except:
            pass
    return {'item': {}, 'desc': {}, 'razao': {}, 'pedido': {}}

def _salvar_cache(cache):
    """Salva cache persistente no disco"""
    try:
        with open(_cache_file, 'wb') as f:
            pickle.dump(cache, f)
    except:
        pass

# Carregar cache
_cache_global = _carregar_cache()
_cache_item = _cache_global.get('item', {})
_cache_desc = _cache_global.get('desc', {})
_cache_razao_social = _cache_global.get('razao', {})
_cache_pedido = _cache_global.get('pedido', {})

def anonimizar_itens(df):
    """
    Anonimiza as colunas 'Item' e 'Desc Item' de forma consistente.
    Usa hash para garantir que o mesmo item sempre gere o mesmo código/descrição falsos.
    """
    categorias_eletronicos = [
        'Monitor', 'Teclado', 'Mouse', 'Webcam', 'Headset', 'Notebook', 
        'Tablet', 'Smartphone', 'Carregador', 'Cabo USB', 'Hub USB',
        'SSD', 'HD Externo', 'Pen Drive', 'Roteador', 'Switch',
        'Impressora', 'Scanner', 'Adaptador', 'Bateria', 'Fonte'
    ]
    
    especificacoes = [
        'LED', 'Wireless', 'Bluetooth', 'RGB', 'USB-C', '4K',
        'Full HD', 'Gamer', 'Pro', 'Plus', 'Ultra', 'Premium'
    ]
    
    def gerar_codigo_item(item_original):
        if pd.isna(item_original):
            return item_original
        if item_original in _cache_item:
            return _cache_item[item_original]
        
        # Usar hash para seed consistente
        seed = int(hashlib.md5(str(item_original).encode()).hexdigest()[:8], 16)
        Faker.seed(seed)
        fake = Faker()
        
        codigo = f"ELET-{fake.random_int(1000, 9999)}-{fake.random_int(100, 999)}"
        _cache_item[item_original] = codigo
        return codigo
    
    def gerar_desc_item(item_original):
        if pd.isna(item_original):
            return item_original
        if item_original in _cache_desc:
            return _cache_desc[item_original]
        
        # Usar hash para seed consistente
        seed = int(hashlib.md5(str(item_original).encode()).hexdigest()[:8], 16)
        Faker.seed(seed)
        fake = Faker()
        
        categoria = fake.random_element(categorias_eletronicos)
        especificacao = fake.random_element(especificacoes)
        tamanho = fake.random_element(['Compacto', 'Standard', 'Grande', ''])
        
        desc = f"{categoria} {especificacao} {tamanho}".strip()
        _cache_desc[item_original] = desc
        return desc
    
    if 'Item' in df.columns:
        df['Item'] = df['Item'].apply(gerar_codigo_item)
    
    if 'Desc Item' in df.columns:
        df['Desc Item'] = df['Desc Item'].apply(gerar_desc_item)
    
    # Salvar cache atualizado
    _salvar_cache({'item': _cache_item, 'desc': _cache_desc, 'razao': _cache_razao_social, 'pedido': _cache_pedido})
    
    return df

def anonimizar_razao_social(df):
    """
    Anonimiza a coluna 'Razao Social' de forma consistente.
    Gera nomes fictícios misturando empresas de eletrônicos e pessoas físicas.
    Usa hash para garantir que a mesma razão social sempre gere o mesmo nome falso.
    """
    # Nomes de empresas fictícias de eletrônicos
    empresas_eletronicos = [
        'TechMax Eletrônicos LTDA',
        'MegaByte Distribuidora',
        'ElectroShop Comércio',
        'Digital Plus Imports',
        'TecnoMundo S.A.',
        'ByteStore Varejo',
        'SmartTech Solutions',
        'GigaStore Eletrônicos',
        'InfoMax Distribuidora',
        'NetWorld Comércio',
        'TechVision Imports',
        'ElectronBay LTDA',
        'DigitalHub Varejo',
        'MegaTech Distribuidora',
        'ByteWare Comércio'
    ]
    
    # Nomes de pessoas fictícias visivelmente falsos
    nomes_pessoas = [
        'João da Silva Eletrônicos',
        'Maria das Neves Tech',
        'José dos Santos Digital',
        'Ana Paula Imports ME',
        'Carlos Alberto Tech Store',
        'Fernanda Lima Eletrônicos',
        'Roberto Carlos Informática',
        'Patricia Souza Digital',
        'Eduardo Pereira Tech',
        'Juliana Costa Imports',
        'Ricardo Santos Eletrônicos',
        'Amanda Oliveira Tech',
        'Bruno Alves Digital',
        'Camila Rodrigues Store',
        'Daniel Martins Tech'
    ]
    
    def gerar_razao_social_falsa(razao_original):
        if pd.isna(razao_original):
            return razao_original
        if razao_original in _cache_razao_social:
            return _cache_razao_social[razao_original]
        
        # Usar hash para seed consistente
        seed = int(hashlib.md5(str(razao_original).encode()).hexdigest()[:8], 16)
        Faker.seed(seed)
        fake = Faker()
        
        # Decidir se será empresa ou pessoa (50/50)
        if fake.random_int(0, 1) == 0:
            # Empresa
            razao_falsa = fake.random_element(empresas_eletronicos)
        else:
            # Pessoa
            razao_falsa = fake.random_element(nomes_pessoas)
        
        _cache_razao_social[razao_original] = razao_falsa
        return razao_falsa
    
    if 'Razao Social' in df.columns:
        df['Razao Social'] = df['Razao Social'].apply(gerar_razao_social_falsa)
    
    # Salvar cache atualizado
    _salvar_cache({'item': _cache_item, 'desc': _cache_desc, 'razao': _cache_razao_social, 'pedido': _cache_pedido})
    
    return df

def anonimizar_pedidos(df):
    """
    Anonimiza a coluna 'Ped Cliente' de forma consistente.
    Gera códigos de pedido fictícios que não fazem referência às marcas reais.
    Usa hash para garantir que o mesmo pedido sempre gere o mesmo código falso.
    """
    # Prefixos neutros para pedidos
    prefixos_pedido = [
        'ELC',  # Eletrônicos
        'TEC',  # Tecnologia
        'DIG',  # Digital
        'INFO', # Informática
        'BYTE', # Byte
        'NET',  # Net
        'WEB',  # Web
        'TECH', # Tech
        'MEGA', # Mega
        'GIGA'  # Giga
    ]
    
    def gerar_pedido_falso(pedido_original):
        if pd.isna(pedido_original):
            return pedido_original
        
        # Tratar caso especial "Sem Pedido"
        if str(pedido_original).strip() == "Sem Pedido":
            return pedido_original
            
        if pedido_original in _cache_pedido:
            return _cache_pedido[pedido_original]
        
        # Usar hash para seed consistente
        seed = int(hashlib.md5(str(pedido_original).encode()).hexdigest()[:8], 16)
        Faker.seed(seed)
        fake = Faker()
        
        # Gerar código de pedido fictício
        prefixo = fake.random_element(prefixos_pedido)
        numero = fake.random_int(10000, 99999)
        pedido_falso = f"{prefixo}-{numero}"
        
        _cache_pedido[pedido_original] = pedido_falso
        return pedido_falso
    
    if 'Ped Cliente' in df.columns:
        df['Ped Cliente'] = df['Ped Cliente'].apply(gerar_pedido_falso)
    
    # Salvar cache atualizado
    _salvar_cache({'item': _cache_item, 'desc': _cache_desc, 'razao': _cache_razao_social, 'pedido': _cache_pedido})
    
    return df

COLUNAS_FATURAMENTO = [
    'Marca', 'Deposito', 'Razao Social', 'Estado', 'Ped Cliente', 'Receita',
    'Situacao Ped', 'Tipo Oper', 'Serie', 'Nota Fiscal', 'Dt Emis NF',
    'Item', 'Desc Item', 'Localização', 'Quantidade', 'Vl Net Livro',
    'Nro Embarque', 'Canal Venda Cliente', 'Dt Embarque'
]


def carregar_dados_faturamento(df_bruto=None, anonimizar=True):
    """
    Carrega dados de faturamento.

    Com `df_bruto` (relatório de faturamento no formato original do ERP, por
    exemplo o arquivo enviado pela tela do dashboard), processa esses dados.
    Sem ele, usa o arquivo de demonstração (cfg.ARQUIVO_DEMO_FATURAMENTO) ou,
    se não existir, o relatório real deixado na pasta (cfg.ARQUIVO_FATURAMENTO).

    `anonimizar=False` mantém item, descrição, razão social e pedido reais.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        arquivo_processado = os.path.join(current_dir, cfg.ARQUIVO_DEMO_FATURAMENTO)
        arquivo_original = os.path.join(current_dir, cfg.ARQUIVO_FATURAMENTO)

        if df_bruto is not None:
            df_faturamento = processar_dados_faturamento(df_bruto[COLUNAS_FATURAMENTO].copy(), anonimizar)
        # Tentar carregar arquivo processado
        elif os.path.exists(arquivo_processado):
            print("⚡ Carregando dados de demonstração...")
            df_faturamento = pd.read_csv(
                arquivo_processado, 
                sep=';', 
                encoding='latin1',
                dtype={'Nota Fiscal': str, 'Nro Embarque': str}
            )
            # Converter datas
            df_faturamento['Dt Emis NF'] = pd.to_datetime(df_faturamento['Dt Emis NF'], errors='coerce')
            df_faturamento['Dt Embarque'] = pd.to_datetime(df_faturamento['Dt Embarque'], errors='coerce')
            print(f"✅ Dados carregados: {len(df_faturamento):,} registros")
        else:
            print("⚠️  Dados de demonstração não encontrados. Processando o relatório da pasta...")
            
            df_faturamento = pd.read_csv(
                arquivo_original,
                sep=';',
                encoding='latin1',
                usecols=COLUNAS_FATURAMENTO,
                dtype={'Nota Fiscal': str, 'Nro Embarque': str}
            )
            df_faturamento = processar_dados_faturamento(df_faturamento, anonimizar)
        
        # Aplicar filtros finais (sempre necessários)
        df_faturamento = df_faturamento[df_faturamento['Serie'].isin(cfg.SERIES_NOTA_FISCAL)]
        df_faturamento = df_faturamento[df_faturamento['Deposito'].isin(cfg.DEPOSITOS_FATURAMENTO)]
        df_faturamento = df_faturamento[~df_faturamento['Desc Item'].isin(cfg.ITENS_EXCLUIDOS)]
        

        # Fill NAs
        df_faturamento.fillna({
            "Ped Cliente": "Sem Pedido", 
            "Nro Embarque": "Sem Embarque",
        }, inplace=True)
        
        return df_faturamento

    except Exception as e:
        print(f"❌ Erro ao carregar dados de faturamento: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def processar_dados_faturamento(df_faturamento, anonimizar=True):
    """
    Processa e limpa os dados de faturamento.
    """
    # Anonimizar dados de Item, Razão Social e Pedidos
    if anonimizar:
        df_faturamento = anonimizar_itens(df_faturamento)
        df_faturamento = anonimizar_razao_social(df_faturamento)
        df_faturamento = anonimizar_pedidos(df_faturamento)
    
    # Converter tipos de dados
    df_faturamento['Serie'] = df_faturamento['Serie'].astype(str)
    df_faturamento = df_faturamento[df_faturamento['Serie'].isin(cfg.SERIES_NOTA_FISCAL)]

    # Esta linha está errada se a intenção é filtrar/remover a marca "?" do DataFrame.
    # O que ela faz: transforma a coluna "Marca" em uma coluna booleana (True/False), destruindo os dados originais.
    # O correto seria filtrar as linhas onde "Marca" não é "?" assim:
    df_faturamento = df_faturamento[df_faturamento["Marca"] != "?"]
    df_faturamento['Deposito'] = df_faturamento['Deposito'].str.upper()
    
    df_faturamento["Marca"].unique()
    # Não, esse trecho não troca valores em branco por 'N/A'.
    # Ele apenas filtra as linhas onde o valor de 'Deposito' (após preencher NaN com 'N/A') é avaliado como True,
    # ou seja, remove linhas onde 'Deposito' é NaN ou string vazia.
    # Para trocar explicitamente valores em branco ou NaN por 'N/A', use:
    df_faturamento['Deposito'] = df_faturamento['Deposito'].replace('', pd.NA).fillna('N/A')
    df_faturamento['Dt Embarque'] = df_faturamento['Dt Embarque'].replace('?', pd.NA).fillna('')
    df_faturamento = df_faturamento[df_faturamento['Deposito'].isin(cfg.DEPOSITOS_FATURAMENTO)]
    
    
    
    df_faturamento['Vl Net Livro'] = para_numero(df_faturamento['Vl Net Livro'])

    # Remover registros onde Localização = 'EXPORTAÇÃO'
    
    # Converter data no formato brasileiro (DD/MM/YYYY)
    df_faturamento['Dt Emis NF'] = para_data(df_faturamento['Dt Emis NF']).dt.normalize()
    df_faturamento['Dt Embarque'] = para_data(df_faturamento['Dt Embarque']).dt.normalize()

    df_faturamento['Quantidade'] = pd.to_numeric(df_faturamento['Quantidade'], errors='coerce').abs()
    
    # Padronizar e categorizar canais de venda
    df_faturamento['Canal Venda Cliente'] = df_faturamento['Canal Venda Cliente'].fillna('N/A')
    
    # Mapeamento de canais: configuracao.MAPEAMENTO_CANAIS
    
    # Aplicar mapeamento
    df_faturamento['Canal Venda Cliente'] = df_faturamento['Canal Venda Cliente'].replace(cfg.MAPEAMENTO_CANAIS)
  
    # Filtrar apenas os tipos de operação permitidos, padronizando o nome da coluna para 'Tipo Oper'
    if 'Tipo Oper' in df_faturamento.columns:
        # Só entram as operações configuradas (configuracao.TIPOS_OPERACAO_FATURAMENTO)
        df_faturamento = df_faturamento[df_faturamento['Tipo Oper'].astype(str).isin(list(cfg.TIPOS_OPERACAO_FATURAMENTO))]

        # Categorizar tipos de operação
        mapeamento_tipo_oper = dict(cfg.TIPOS_OPERACAO_FATURAMENTO)
        
        # Aplicar categorização
        df_faturamento['Tipo Oper'] = df_faturamento['Tipo Oper'].replace(mapeamento_tipo_oper)
        
        df_faturamento['Tipo Oper'].groupby(df_faturamento['Marca']).value_counts()
    # Limpar dados

    # Aplicar filtros iniciais para faturamento
    df_faturamento.fillna({
        "Ped Cliente": "Sem Pedido", 
        "Nro Embarque": "Sem Embarque",
    }, inplace=True)
    
    
    
    df_faturamento = df_faturamento[~df_faturamento['Desc Item'].isin(cfg.ITENS_EXCLUIDOS)]
    
        # Filtrar marcas indesejadas
    if "Marca" in df_faturamento.columns:
        df_faturamento = df_faturamento[~df_faturamento["Marca"].isin(cfg.MARCAS_EXCLUIDAS)]
    return df_faturamento


def obter_css_cards():
    """
    Retorna o CSS para estilização de cards.
    
    Returns:
        str: CSS para cards
    """
    css = """
    <style>
    .card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 15px;
        margin: 5px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        flex: 1;
        min-width: 0;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }

    .card-title {
        color: white;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
        text-align: center;
    }

    .card-value {
        color: white;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }

    .card-subtitle {
        color: rgba(255,255,255,0.8);
        font-size: 11px;
        text-align: center;
    }

    .metric-container {
        display: flex;
        flex-wrap: nowrap;
        gap: 10px;
        justify-content: space-between;
        margin: 20px 0;
        width: 100%;
    }

    .card {
        flex: 1;
        min-width: 0;
    }
    </style>
    """
    return css


# =============================================================================
# FUNÇÕES PARA SEPARAÇÃO DE RECEITA SIM E RECEITA NÃO
# =============================================================================

def obter_tipos_receita_sim():
    """
    Retorna a lista de tipos de operação considerados como Receita Sim.
    
    Returns:
        list: Lista de tipos de operação de receita normal.
    """
    return [
        "RECEITA DIRETA",
        "RECEITA REVENDA",
    ]

def obter_tipos_receita_nao():
    """
    Retorna a lista de tipos de operação considerados como Receita Não.
    
    Returns:
        list: Lista de tipos de operação de receita não (brindes/transferências).
    """
    return [
        "BONIFICAÇÃO", 
        "TRANSFERÊNCIA"
    ]

def filtrar_receita_sim(df_faturamento):
    """
    Filtra o DataFrame para incluir apenas registros de Receita Sim.
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        
    Returns:
        pd.DataFrame: DataFrame filtrado apenas com receitas normais.
    """
    if 'Tipo Oper' not in df_faturamento.columns:
        return pd.DataFrame()
    
    tipos_receita_sim = obter_tipos_receita_sim()
    return df_faturamento[df_faturamento['Tipo Oper'].astype(str).isin(tipos_receita_sim)]

def filtrar_receita_nao(df_faturamento):
    """
    Filtra o DataFrame para incluir apenas registros de Receita Não.
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        
    Returns:
        pd.DataFrame: DataFrame filtrado apenas com brindes e transferências.
    """
    if 'Tipo Oper' not in df_faturamento.columns:
        return pd.DataFrame()
    
    tipos_receita_nao = obter_tipos_receita_nao()
    return df_faturamento[df_faturamento['Tipo Oper'].astype(str).isin(tipos_receita_nao)]

def analisar_receita_sim_por_marca(df_faturamento):
    """
    Analisa o faturamento de Receita Sim por marca.
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        
    Returns:
        pd.DataFrame: DataFrame com análise de receita sim por marca.
    """
    df_receita_sim = filtrar_receita_sim(df_faturamento)
    
    if df_receita_sim.empty:
        return pd.DataFrame(columns=['Marca', 'Receita Sim', 'QTD. NFs'])
    
    # Consolidar notas fiscais duplicadas primeiro
    df_consolidado = (
        df_receita_sim.groupby(['Nota Fiscal', 'Marca'])['Vl Net Livro']
        .sum()
        .reset_index()
    )
    
    # Agrupar por marca
    analise_por_marca = df_consolidado.groupby('Marca').agg({
        'Vl Net Livro': 'sum',
        'Nota Fiscal': 'nunique'
    }).reset_index()
    
    # Renomear colunas
    analise_por_marca.columns = ['Marca', 'Receita Sim', 'QTD. NFs']
    
    # Ordenar por receita sim (decrescente)
    analise_por_marca = analise_por_marca.sort_values('Receita Sim', ascending=False)
    
    return analise_por_marca

def analisar_receita_nao_por_marca(df_faturamento):
    """
    Analisa o faturamento de Receita Não por marca.
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        
    Returns:
        pd.DataFrame: DataFrame com análise de receita não por marca.
    """
    df_receita_nao = filtrar_receita_nao(df_faturamento)
    
    if df_receita_nao.empty:
        return pd.DataFrame(columns=['Marca', 'Receita Não', 'QTD. NFs (NÃO)'])
    
    # Consolidar notas fiscais duplicadas primeiro
    df_consolidado = (
        df_receita_nao.groupby(['Nota Fiscal', 'Marca'])['Vl Net Livro']
        .sum()
        .reset_index()
    )
    
    # Agrupar por marca
    analise_por_marca = df_consolidado.groupby('Marca').agg({
        'Vl Net Livro': 'sum',
        'Nota Fiscal': 'nunique'
    }).reset_index()
    
    # Renomear colunas
    analise_por_marca.columns = ['Marca', 'Receita Não', 'QTD. NFs (NÃO)']
    
    # Ordenar por receita não (decrescente)
    analise_por_marca = analise_por_marca.sort_values('Receita Não', ascending=False)
    
    return analise_por_marca

def analisar_receita_completa_por_marca(df_faturamento):
    """
    Analisa tanto Receita Sim quanto Receita Não por marca em um único DataFrame.
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        
    Returns:
        pd.DataFrame: DataFrame com análise completa de receita sim e não por marca.
    """
    # Obter análises separadas
    df_receita_sim = analisar_receita_sim_por_marca(df_faturamento)
    df_receita_nao = analisar_receita_nao_por_marca(df_faturamento)
    
    # Fazer merge das duas análises
    df_completo = df_receita_sim.merge(
        df_receita_nao, 
        on='Marca', 
        how='outer'
    ).fillna(0)
    
    # Ordenar por receita sim (decrescente)
    df_completo = df_completo.sort_values('Receita Sim', ascending=False)
    
    return df_completo

def lead_time(df_faturamento):
    """
    Calcula o lead time (tempo entre geração do embarque e emissão da NF) em dias úteis.
    Valores de Lead Time > 5 são automaticamente limitados a 5 para consistência com a classificação D+.
    

    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        
    Returns:
        pd.DataFrame: DataFrame com análise de lead time por marca e métricas agregadas.
    """
    import numpy as np
    from datetime import datetime, timedelta
    
    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Tipo Oper', 'Marca', 'Nro Embarque', 'Dt Embarque', 'Dt Emis NF', 'Canal Venda Cliente']
    colunas_existentes = [col for col in colunas_necessarias if col in df_faturamento.columns]
    
    if len(colunas_existentes) < 5:
        return pd.DataFrame(columns=['Marca', 'Lead Time Médio (dias úteis)', 'Qtd Registros', 'Lead Time Min', 'Lead Time Max'])
    
    # Aplicar filtros específicos
    df_filtrado = df_faturamento.copy()
    
    # 1. Filtro de Receita = SIM
    tipos_receita_sim = obter_tipos_receita_sim()
    df_filtrado = df_filtrado[df_filtrado['Tipo Oper'].astype(str).isin(tipos_receita_sim)]
    
    # 2. Filtro de Marca = UNIDADE SOROCABA, SAO PAULO, FLORIANOPOLIS
    marcas_permitidas = ['UNIDADE SOROCABA', 'UNIDADE SAO PAULO', 'UNIDADE FLORIANOPOLIS']
    df_filtrado = df_filtrado[df_filtrado['Marca'].isin(marcas_permitidas)]
    
    # 3. Filtro de Nro Embarque != "Sem Embarque"
    df_filtrado = df_filtrado[df_filtrado['Nro Embarque'] != 'Sem Embarque']
    
    if df_filtrado.empty:
        return pd.DataFrame(columns=['Marca', 'Lead Time Médio (dias úteis)', 'Qtd Registros', 'Lead Time Min', 'Lead Time Max'])
    
    # Exclui vendas internas (o canal já mapeado e os códigos que viram "VENDA INTERNA")
    vendas_internas = ['VENDA INTERNA'] + [k for k, v in cfg.MAPEAMENTO_CANAIS.items() if v == 'VENDA INTERNA']
    df_filtrado = df_filtrado[~df_filtrado['Canal Venda Cliente'].isin(vendas_internas)]
    
    # Converter datas para datetime se necessário
    df_filtrado['Dt Embarque'] = pd.to_datetime(df_filtrado['Dt Embarque'], errors='coerce')
    df_filtrado['Dt Emis NF'] = pd.to_datetime(df_filtrado['Dt Emis NF'], errors='coerce')
    
    # Remover duplicatas de Nota Fiscal, mantendo apenas o primeiro registro de cada Nota Fiscal
    if 'Nota Fiscal' in df_filtrado.columns:
        df_filtrado = df_filtrado.drop_duplicates(subset=['Nota Fiscal'])
    
    # Remover registros com datas inválidas
    df_filtrado = df_filtrado.dropna(subset=['Dt Embarque', 'Dt Emis NF'])
    
    if df_filtrado.empty:
        return pd.DataFrame(columns=['Marca', 'Lead Time Médio (dias úteis)', 'Qtd Registros', 'Lead Time Min', 'Lead Time Max'])
    
    def calcular_dias_uteis(data_inicio, data_fim):
        """
        Calcula o número de dias úteis entre duas datas.
        Se o resultado for negativo, retorna 0.
        """
        if pd.isna(data_inicio) or pd.isna(data_fim):
            return 0
        
        # Se data de embarque é anterior à data de emissão da NF, retornar 0
        if data_fim < data_inicio:
            return 0
        
        # Calcular diferença em dias
        diferenca_dias = (data_fim - data_inicio).days
        
        # Se diferença é negativa ou zero, retornar 0
        if diferenca_dias <= 0:
            return 0
        
        # Calcular dias úteis (excluindo finais de semana)
        dias_uteis = 0
        data_atual = data_inicio
        
        while data_atual < data_fim:
            # Verificar se não é sábado (5) nem domingo (6)
            if data_atual.weekday() < 5:  # 0=segunda, 1=terça, ..., 4=sexta
                dias_uteis += 1
            data_atual += timedelta(days=1)
        
        return dias_uteis
    
    # Calcular lead time para cada registro
    df_filtrado['Lead Time'] = df_filtrado.apply(
        lambda row: calcular_dias_uteis(row['Dt Embarque'], row['Dt Emis NF']), 
        axis=1
    )
    
    # CORREÇÃO: Limitar Lead Time a máximo de 5 dias (igual à classificação D+)
    df_filtrado['Lead Time'] = df_filtrado['Lead Time'].apply(lambda x: min(x, 5) if pd.notna(x) else x)
    
    # Remover registros com lead time = 0 (casos onde NF foi emitida antes do embarque)
    df_filtrado = df_filtrado[df_filtrado['Lead Time'] > 0]
    
    if df_filtrado.empty:
        return pd.DataFrame(columns=['Marca', 'Lead Time Médio (dias úteis)', 'Qtd Registros', 'Lead Time Min', 'Lead Time Max'])
    
    # Agrupar por marca e calcular métricas
    analise_lead_time = df_filtrado.groupby('Marca').agg({
        'Lead Time': ['mean', 'min', 'max', 'count'],
        'Nota Fiscal': 'nunique'
    }).reset_index()
    
    # Flatten das colunas multi-level
    analise_lead_time.columns = ['Marca', 'Lead Time Médio', 'Lead Time Min', 'Lead Time Max', 'Qtd Registros', 'Qtd NFs Únicas']
    
    # Arredondar lead time médio para 1 casa decimal
    analise_lead_time['Lead Time Médio'] = analise_lead_time['Lead Time Médio'].round(1)
    
    # Renomear colunas para exibição
    analise_lead_time = analise_lead_time.rename(columns={
        'Lead Time Médio': 'Lead Time Médio (dias úteis)',
        'Lead Time Min': 'Lead Time Min',
        'Lead Time Max': 'Lead Time Max'
    })
    
    # Ordenar por lead time médio (crescente - menor lead time primeiro)
    analise_lead_time = analise_lead_time.sort_values('Lead Time Médio (dias úteis)', ascending=True)
    
    return analise_lead_time


# Converter valores monetários do formato brasileiro para float corretamente

# 🪄 Função para formatar valores
def formatar_valor_seguro(valor, tipo="currency"):
    try:
        if tipo == "currency":
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        elif tipo == "number":
            return f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            return str(valor)
    except:
        return str(valor)

# =============================================================================
# FUNÇÕES DE CUT-OFF E MAPEAMENTO DE REGIÕES
# =============================================================================

def obter_cut_off_por_mes(meses_filtro):
    """
    Retorna o cut-off total para os meses especificados usando valores fixos históricos
    
    Args:
        meses_filtro (list): Lista de meses para calcular o cut-off
        
    Returns:
        float: Valor total do cut-off para os meses especificados
    """
    total_cut_off = 0
    for mes in meses_filtro:
        total_cut_off += get_cut_off_total_mensal(mes)
    return total_cut_off

def obter_cut_off_por_marca_mes(marca, mes):
    """
    Retorna o cut-off de uma marca específica em um mês específico
    
    Args:
        marca (str): Nome da unidade (ex: 'UNIDADE SOROCABA')
        mes (str): Nome do mês (ex: 'Janeiro')
        
    Returns:
        float: Valor do cut-off para a marca no mês especificado
    """
    return get_cut_off_mensal(mes, marca)

def obter_regiao_por_estado(estado):
    """
    Retorna a região brasileira para um estado específico.
    Pode ser usada para mapear tanto em diferentes datasets, padronizando o nome da coluna de região.

    Args:
        estado (str): Sigla do estado ou 'EXPORTAÇÃO'

    Returns:
        str: Nome da região (Norte, Nordeste, Centro-Oeste, Sudeste, Sul, Exportação)
    """
    mapeamento_estados_regioes = {
        # Região Norte
        'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 
        'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
        
        # Região Nordeste
        'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
        'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
        
        # Região Centro-Oeste
        'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
        
        # Região Sudeste
        'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
        
        # Região Sul
        'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
        
        # Exportação
        'EXPORTAÇÃO': 'Exportação', 'EXPORTACAO': 'Exportação', 'EXPORT': 'Exportação'
    }
    if pd.isna(estado):
        return 'Não Informado'
    estado_str = str(estado).strip().upper()
    return mapeamento_estados_regioes.get(estado_str, 'Outros')

def obter_cores_marca():
    """
    Retorna um dicionário com as cores padronizadas para cada marca.

    Returns:
        dict: Dicionário com o nome da marca como chave e a cor como valor.
    """
    return {
        # Paleta do design system (ui_theme.SEQUENCIA_CATEGORICA): tons distinguíveis
        # entre si e com contraste >= 3:1 sobre fundo branco.
        "UNIDADE SOROCABA": "#1E40AF",           # azul
        "UNIDADE SAO PAULO": "#DC2626",          # vermelho
        "UNIDADE FLORIANOPOLIS": "#D97706",      # âmbar
        "UNIDADE CURITIBA": "#059669",           # verde
        "UNIDADE PORTO ALEGRE": "#7C3AED",       # violeta
        "UNIDADE BRASILIA": "#0891B2",           # ciano
        "Total": "#0F172A",                      # grafite
    }

def exibir_cards_faturamento_por_marca_bruto(df_faturamento):
    """
    Agrupa o DataFrame por marca, calcula o total por marca e retorna um DataFrame
    com as colunas padronizadas ('Marca' e 'Valor') para evitar erros de leitura.
    
    Trata notas fiscais duplicadas consolidando os valores por NF antes do agrupamento por marca.

    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.

    Returns:
        pd.DataFrame: DataFrame com colunas 'Marca' e 'Valor' (total por marca).
    """
    # Verifica se as colunas necessárias existem
    if "Marca" not in df_faturamento.columns or "Vl Net Livro" not in df_faturamento.columns or "Nota Fiscal" not in df_faturamento.columns:
        raise ValueError("O DataFrame deve conter as colunas 'Marca', 'Vl Net Livro' e 'Nota Fiscal'.")

    # Primeiro, consolidar notas fiscais duplicadas
    # Agrupa por Nota Fiscal e Marca, somando TODOS os valores dos itens da mesma NF
    df_consolidado = (
        df_faturamento.groupby(['Nota Fiscal', 'Marca'])['Vl Net Livro']
        .sum()  # Soma todos os itens da mesma NF
        .reset_index()
    )
    
    
    # Renomear a coluna para Valor_NF_NET
    df_consolidado = df_consolidado.rename(columns={"Vl Net Livro": "Valor_NF_NET"})
    # Remover duplicatas de Nota Fiscal
    df_consolidado = df_consolidado.drop_duplicates(subset=['Nota Fiscal'])
    # Agora agrupa por marca e soma o valor consolidado das NFs
    faturamento_por_marca = (
        df_consolidado.groupby(df_consolidado['Marca'].astype(str))['Valor_NF_NET']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    
    # Padroniza o nome da coluna de valor para 'Valor'
    faturamento_por_marca = faturamento_por_marca.rename(columns={"Valor_NF_NET": "Valor"})

    return faturamento_por_marca

def notas_fiscais_emitidas_por_marca(df_faturamento):
    """
    Retorna a quantidade de notas fiscais únicas por marca, tratando duplicatas.

    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.

    Returns:
        pd.DataFrame: DataFrame com colunas 'Marca' e 'Notas_Fiscais' (quantidade de NFs únicas por marca).
    """
    # Verifica se as colunas necessárias existem
    if "Marca" not in df_faturamento.columns or "Nota Fiscal" not in df_faturamento.columns:
        raise ValueError("O DataFrame deve conter as colunas 'Marca' e 'Nota Fiscal'.")

    # Seleciona apenas as colunas relevantes e remove duplicatas de NF+Marca
    df_unicas = df_faturamento[['Marca', 'Nota Fiscal']].drop_duplicates()

    # Conta quantas notas fiscais únicas existem por marca
    notas_por_marca = (
        df_unicas.groupby('Marca')['Nota Fiscal']
        .nunique()
        .sort_values(ascending=False)
        .reset_index()
    )

    # Padroniza o nome da coluna para 'Notas_Fiscais'
    notas_por_marca = notas_por_marca.rename(columns={"Nota Fiscal": "Notas_Fiscais"})

    return notas_por_marca

def calcular_faturamento_bruto_liquido_por_marca_mes(df_faturamento, marca_selecionada):
    """
    Calcula faturamento bruto e líquido por mês para uma marca específica.
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        marca_selecionada (str): Nome da marca para calcular.
        
    Returns:
        pd.DataFrame: DataFrame com colunas 'Mês_Str', 'Vl Net Livro', 'Tipo' para gráfico comparativo.
    """
    # Verifica se as colunas necessárias existem
    colunas_necessarias = ['Marca', 'Dt Emis NF', 'Vl Net Livro', 'Tipo Oper']
    colunas_existentes = [col for col in colunas_necessarias if col in df_faturamento.columns]
    
    if len(colunas_existentes) < 4:
        return pd.DataFrame()
    
    # Filtrar dados da marca selecionada
    dados_marca = df_faturamento[df_faturamento['Marca'] == marca_selecionada].copy()
    
    if dados_marca.empty:
        return pd.DataFrame()
    
    # Adicionar colunas de mês
    dados_marca['Mês'] = dados_marca['Dt Emis NF'].dt.to_period('M')
    dados_marca['Mês_Str'] = dados_marca['Mês'].astype(str)
    
    # Calcular faturamento bruto por mês
    dados_bruto = dados_marca.groupby('Mês_Str')['Vl Net Livro'].sum().reset_index()
    dados_bruto['Tipo'] = 'Faturamento Bruto'
    
    # Calcular devoluções por mês
    devolucao_filtros = ['DEVOLUÇÃO']
    dados_devolucao = dados_marca[dados_marca['Tipo Oper'].isin(devolucao_filtros)]
    dados_devolucao_agrupados = dados_devolucao.groupby('Mês_Str')['Vl Net Livro'].sum().reset_index()
    dados_devolucao_agrupados['Tipo'] = 'Devoluções'
    
    # Debug: verificar se há devoluções
    print(f"DEBUG - Devoluções encontradas para {marca_selecionada}: {len(dados_devolucao)} registros")
    if not dados_devolucao.empty:
        print(f"DEBUG - Tipos de operação de devolução: {dados_devolucao['Tipo Oper'].unique()}")
        print(f"DEBUG - Total devoluções: {dados_devolucao['Vl Net Livro'].sum()}")
    else:
        print("DEBUG - Nenhuma devolução encontrada")
    
    # Calcular cut-off específico para a marca selecionada
    dados_cut_off = _calcular_cut_off_por_marca_mes(marca_selecionada, dados_bruto['Mês_Str'].unique())
    
    # Debug: verificar cut-off
    print(f"DEBUG - Cut-off calculado: {dados_cut_off['Vl Net Livro'].sum()}")
    print(f"DEBUG - Cut-off por mês: {dados_cut_off[['Mês_Str', 'Vl Net Livro']].to_string()}")
    
    # Calcular faturamento líquido (bruto - devolução - cut-off)
    dados_liquido = dados_bruto.copy()
    
    # Fazer merge para alinhar os dados por mês
    dados_liquido = dados_liquido.merge(
        dados_devolucao_agrupados[['Mês_Str', 'Vl Net Livro']], 
        on='Mês_Str', 
        how='left', 
        suffixes=('', '_devolucao')
    )
    dados_liquido = dados_liquido.merge(
        dados_cut_off[['Mês_Str', 'Vl Net Livro']], 
        on='Mês_Str', 
        how='left', 
        suffixes=('', '_cutoff')
    )
    
    # Preencher valores nulos com zero
    dados_liquido['Vl Net Livro_devolucao'] = dados_liquido['Vl Net Livro_devolucao'].fillna(0)
    dados_liquido['Vl Net Livro_cutoff'] = dados_liquido['Vl Net Livro_cutoff'].fillna(0)
    
    # Calcular faturamento líquido
    dados_liquido['Vl Net Livro'] = dados_liquido['Vl Net Livro'] - dados_liquido['Vl Net Livro_devolucao'] - dados_liquido['Vl Net Livro_cutoff']
    dados_liquido['Tipo'] = 'Faturamento Líquido'
    
    # Debug: verificar cálculo do líquido
    print(f"DEBUG - Faturamento bruto total: {dados_bruto['Vl Net Livro'].sum()}")
    print(f"DEBUG - Faturamento líquido total: {dados_liquido['Vl Net Livro'].sum()}")
    print(f"DEBUG - Diferença: {dados_bruto['Vl Net Livro'].sum() - dados_liquido['Vl Net Livro'].sum()}")
    
    # Manter apenas as colunas necessárias
    dados_liquido = dados_liquido[['Mês_Str', 'Vl Net Livro', 'Tipo']]
    
    # Combinar bruto e líquido para o gráfico
    dados_grafico = pd.concat([dados_bruto, dados_liquido], ignore_index=True)
    
    return dados_grafico

def analisar_faturamento_por_unidade_negocio(df_faturamento):
    """
    Analisa o faturamento por unidade de negócio (marca) com métricas detalhadas.
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        
    Returns:
        pd.DataFrame: DataFrame com análise por unidade de negócio.
    """
    # Verifica se as colunas necessárias existem
    if "Marca" not in df_faturamento.columns or "Vl Net Livro" not in df_faturamento.columns or "Nota Fiscal" not in df_faturamento.columns:
        raise ValueError("O DataFrame deve conter as colunas 'Marca', 'Vl Net Livro' e 'Nota Fiscal'.")
    
    # Consolidar notas fiscais duplicadas primeiro
    df_consolidado = (
        df_faturamento.groupby(['Nota Fiscal', 'Marca'])['Vl Net Livro']
        .sum()
        .reset_index()
    )
    
    # Agrupar por marca e calcular métricas
    analise_por_marca = df_consolidado.groupby('Marca').agg({
        'Vl Net Livro': 'sum',           # Valor total
        'Nota Fiscal': 'nunique'         # Quantidade de NFs únicas
    }).reset_index()
    
    # Calcular ticket médio
    analise_por_marca['Ticket_Medio'] = analise_por_marca['Vl Net Livro'] / analise_por_marca['Nota Fiscal']
    
    # Renomear colunas para o padrão
    analise_por_marca = analise_por_marca.rename(columns={
        'Marca': 'Unidade_de_Negocio',
        'Vl Net Livro': 'VALOR_NET',
        'Nota Fiscal': 'QTD_NFs',
        'Ticket_Medio': 'Ticket_Medio'
    })
    
    # Ordenar por valor total (maior para menor)
    analise_por_marca = analise_por_marca.sort_values('VALOR_NET', ascending=False)
    
    return analise_por_marca

def analisar_faturamento_por_canal_venda(df_faturamento):
    """
    Analisa o faturamento por canal de venda com métricas detalhadas.
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        
    Returns:
        pd.DataFrame: DataFrame com análise por canal de venda.
    """
    # Verifica se as colunas necessárias existem
    if "Canal Venda Cliente" not in df_faturamento.columns or "Vl Net Livro" not in df_faturamento.columns or "Nota Fiscal" not in df_faturamento.columns:
        raise ValueError("O DataFrame deve conter as colunas 'Canal Venda Cliente', 'Vl Net Livro' e 'Nota Fiscal'.")
    
    # Consolidar notas fiscais duplicadas primeiro
    df_consolidado = (
        df_faturamento.groupby(['Nota Fiscal', 'Canal Venda Cliente'])['Vl Net Livro']
        .sum()
        .reset_index()
    )
    
    # Agrupar por canal de venda e calcular métricas
    analise_por_canal = df_consolidado.groupby('Canal Venda Cliente').agg({
        'Vl Net Livro': 'sum',           # Valor total
        'Nota Fiscal': 'nunique'         # Quantidade de NFs únicas
    }).reset_index()
    
    # Calcular ticket médio
    analise_por_canal['Ticket_Medio'] = analise_por_canal['Vl Net Livro'] / analise_por_canal['Nota Fiscal']
    
    # Renomear colunas para o padrão
    analise_por_canal = analise_por_canal.rename(columns={
        'Canal Venda Cliente': 'Canal_Venda',
        'Vl Net Livro': 'VALOR_NET',
        'Nota Fiscal': 'QTD_NFs',
        'Ticket_Medio': 'Ticket_Medio'
    })
    
    # Ordenar por valor total (maior para menor)
    analise_por_canal = analise_por_canal.sort_values('VALOR_NET', ascending=False)
    
    return analise_por_canal

def analisar_canal_venda_por_marca(df_faturamento):
    """
    Analisa o faturamento por canal de venda agrupado por marca (hierárquico).
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento.
        
    Returns:
        dict: Dicionário com DataFrames por marca contendo total + canais de venda.
    """
    # Verifica se as colunas necessárias existem
    if "Marca" not in df_faturamento.columns or "Canal Venda Cliente" not in df_faturamento.columns or "Vl Net Livro" not in df_faturamento.columns or "Nota Fiscal" not in df_faturamento.columns:
        raise ValueError("O DataFrame deve conter as colunas 'Marca', 'Canal Venda Cliente', 'Vl Net Livro' e 'Nota Fiscal'.")
    
    # Consolidar notas fiscais duplicadas primeiro
    df_consolidado = (
        df_faturamento.groupby(['Nota Fiscal', 'Marca', 'Canal Venda Cliente'])['Vl Net Livro']
        .sum()
        .reset_index()
    )
    
    # Dicionário para armazenar resultados finais por marca
    resultados_finais = {}
    
    # Calcular total por marca primeiro
    totais_por_marca = df_consolidado.groupby('Marca').agg({
        'Vl Net Livro': 'sum',
        'Nota Fiscal': 'nunique'
    }).reset_index()
    
    # Iterar por marca
    for marca in totais_por_marca['Marca']:
        # Dados do total da marca
        total_marca = totais_por_marca[totais_por_marca['Marca'] == marca]
        valor_total = total_marca['Vl Net Livro'].iloc[0]
        qtd_nfs_total = total_marca['Nota Fiscal'].iloc[0]
        ticket_medio_total = valor_total / qtd_nfs_total
        
        # Criar DataFrame final para esta marca
        df_final = []
        
        # Adicionar linha do total da marca
        df_final.append({
            'Unidade_Negocio': marca,
            'VALOR_NET': valor_total,
            'QTD_NFs': qtd_nfs_total,
            'Ticket_Medio': ticket_medio_total
        })
        
        # Filtrar dados da marca específica
        dados_marca = df_consolidado[df_consolidado['Marca'] == marca].copy()
        
        # Agrupar por canal de venda dentro da marca
        analise_canal = dados_marca.groupby('Canal Venda Cliente').agg({
            'Vl Net Livro': 'sum',
            'Nota Fiscal': 'nunique'
        }).reset_index()
        
        # Calcular ticket médio por canal
        analise_canal['Ticket_Medio'] = analise_canal['Vl Net Livro'] / analise_canal['Nota Fiscal']
        
        # Renomear colunas
        analise_canal = analise_canal.rename(columns={
            'Canal Venda Cliente': 'Unidade_Negocio',
            'Vl Net Livro': 'VALOR_NET',
            'Nota Fiscal': 'QTD_NFs'
        })
        
        # Ordenar canais por valor (maior para menor)
        analise_canal = analise_canal.sort_values('VALOR_NET', ascending=False)
        
        # Adicionar canais ao DataFrame final
        df_final.extend(analise_canal.to_dict('records'))
        
        # Converter para DataFrame e armazenar
        df_final = pd.DataFrame(df_final)
        df_final = df_final.sort_values('VALOR_NET', ascending=False)
        
        resultados_finais[marca] = df_final
    
    return resultados_finais

def _calcular_cut_off_por_marca_mes(marca_selecionada, meses_unicos):
    """
    Função auxiliar para calcular cut-off por marca e mês.
    
    Args:
        marca_selecionada (str): Nome da marca.
        meses_unicos (list): Lista de meses únicos no formato 'YYYY-MM'.
        
    Returns:
        pd.DataFrame: DataFrame com cut-off por mês.
    """
    try:
        # Criar dicionário de mapeamento de meses
        mapeamento_meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        # As unidades já estão padronizadas (UNIDADE SOROCABA, etc.)
        marca_cut_off = marca_selecionada
        
        if marca_cut_off:
            # Criar DataFrame com cut-off por mês usando valores fixos históricos
            dados_cut_off = []
            for mes_str in meses_unicos:
                try:
                    ano, mes = mes_str.split('-')
                    mes_num = int(mes)
                    mes_nome = mapeamento_meses.get(mes_num, '')
                    if mes_nome:
                        cut_off_mes = obter_cut_off_por_marca_mes(marca_cut_off, mes_nome)
                        dados_cut_off.append({
                            'Mês_Str': mes_str,
                            'Vl Net Livro': cut_off_mes,
                            'Tipo': 'Cut-off'
                        })
                except:
                    dados_cut_off.append({
                        'Mês_Str': mes_str,
                        'Vl Net Livro': 0,
                        'Tipo': 'Cut-off'
                    })
            
            return pd.DataFrame(dados_cut_off)
        else:
            # Se não houver marca correspondente, usar zeros
            return pd.DataFrame({
                'Mês_Str': list(meses_unicos),
                'Vl Net Livro': [0] * len(meses_unicos),
                'Tipo': 'Cut-off'
            })
            
    except Exception as e:
        # Se não conseguir carregar cut-off, usar zeros
        return pd.DataFrame({
            'Mês_Str': list(meses_unicos),
            'Vl Net Livro': [0] * len(meses_unicos),
            'Tipo': 'Cut-off'
        })


# Cria colunas 'Lead Time' e 'D+' - Lead Time em dias úteis entre 'Dt Emis NF' e 'Dt Embarque'
# D+ classifica o lead time: D+0 a D+5 (valores >5 agrupados como D+5)
def adicionar_lead_time(df):
    """
    Adiciona colunas 'Lead Time' e 'D+' ao DataFrame.
    Lead Time: diferença em dias úteis entre 'Dt Emis NF' e 'Dt Embarque', limitado a máximo de 5 dias.
    D+: classificação do lead time (D+0 a D+5, valores >5 agrupados como D+5).
    Exclui sábados e domingos do cálculo.
    Valores de Lead Time > 5 são automaticamente limitados a 5 para consistência com a classificação D+.
    """
    if 'Dt Embarque' in df.columns and 'Dt Emis NF' in df.columns:
        # Garante que as colunas estão no formato datetime
        df = df.copy()
        df['Dt Embarque'] = pd.to_datetime(df['Dt Embarque'], errors='coerce')
        df['Dt Emis NF'] = pd.to_datetime(df['Dt Emis NF'], errors='coerce')
        
        # Se Dt Embarque for None, usar o valor de Dt Emis NF
        df['Dt Embarque'] = df['Dt Embarque'].fillna(df['Dt Emis NF'])
        
        # Calcula o lead time apenas em dias úteis (excluindo sábados e domingos)
        def calcular_dias_uteis(data_inicio, data_fim):
            if pd.isna(data_inicio) or pd.isna(data_fim):
                return 0
            if data_fim < data_inicio:
                return 0
            
            # Se for o mesmo dia, lead time é 0
            if data_inicio.date() == data_fim.date():
                return 0
            
            # Usar pd.bdate_range para contar apenas dias úteis
            try:
                # Usar inclusive='right' para incluir o dia final mas não o inicial
                # Isso conta os dias úteis desde o dia seguinte ao embarque até o dia da NF
                dias_uteis = pd.bdate_range(start=data_inicio, end=data_fim, inclusive='right')
                return len(dias_uteis)
            except Exception as e:
                # Em caso de erro, retornar diferença simples em dias
                return max(0, (data_fim - data_inicio).days)
        
        df['Lead Time'] = df.apply(
            lambda row: calcular_dias_uteis(row['Dt Embarque'], row['Dt Emis NF']), 
            axis=1
        )
        
        # CORREÇÃO: Limitar Lead Time a máximo de 5 dias (igual à classificação D+)
        df['Lead Time'] = df['Lead Time'].apply(lambda x: min(x, 5) if pd.notna(x) else x)
        
        # Criar coluna D+ baseada no Lead Time
        def criar_coluna_d_mais(lead_time):
            if pd.isna(lead_time):
                return 'N/A'
            elif lead_time == 0:
                return 'D+0'
            elif lead_time == 1:
                return 'D+1'
            elif lead_time == 2:
                return 'D+2'
            elif lead_time == 3:
                return 'D+3'
            elif lead_time == 4:
                return 'D+4'
            elif lead_time == 5:
                return 'D+5'
            else:
                return 'D+5'  # Valores maiores que 5 são agrupados como D+5
        
        df['D+'] = df['Lead Time'].apply(criar_coluna_d_mais)
        
    else:
        df['Lead Time'] = pd.NA
        df['D+'] = 'N/A'
    return df

# Calcular a média do lead time (ignorando valores nulos)
def media_lead_time(df):
    """
    Calcula a média do lead time (em dias) do DataFrame fornecido.
    Considera apenas valores válidos (não nulos) na coluna 'Lead Time'.
    Retorna float (média) ou None se não houver valores válidos.
    """
    if 'Lead Time' not in df.columns:
        return None
    media = df['Lead Time'].dropna()
    if len(media) == 0:
        return None
    return media.mean()

def calcular_nfs_acumuladas(df_faturamento):
    """
    Calcula as notas fiscais acumuladas por dia e por marca.
    
    Args:
        df_faturamento (pd.DataFrame): DataFrame de faturamento filtrado.
        
    Returns:
        tuple: (df_geral, df_marca) onde:
            - df_geral: DataFrame com colunas 'Data', 'NFs_Dia', 'NFs_Acumuladas_Geral'
            - df_marca: DataFrame com colunas 'Data', 'Marca', 'NFs_Acumuladas_Por_Marca'
    """
    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Dt Emis NF', 'Nota Fiscal', 'Marca']
    colunas_existentes = [col for col in colunas_necessarias if col in df_faturamento.columns]
    
    if len(colunas_existentes) < 3:
        return pd.DataFrame(), pd.DataFrame()
    
    # Criar cópia do DataFrame para não modificar o original
    df_temp = df_faturamento.copy()
    
    # Converter data para datetime se necessário
    df_temp['Dt Emis NF'] = pd.to_datetime(df_temp['Dt Emis NF'], errors='coerce')
    
    # Remover registros com data inválida
    df_temp = df_temp.dropna(subset=['Dt Emis NF'])
    
    if df_temp.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # Remover duplicatas de Nota Fiscal por dia (uma NF pode ter múltiplos itens)
    df_unicas = df_temp[['Dt Emis NF', 'Nota Fiscal', 'Marca']].drop_duplicates()
    
    # Agrupar por data e contar NFs únicas
    nfs_por_dia = df_unicas.groupby('Dt Emis NF')['Nota Fiscal'].nunique().reset_index()
    nfs_por_dia.columns = ['Data', 'NFs_Dia']
    
    # Ordenar por data
    nfs_por_dia = nfs_por_dia.sort_values('Data')
    
    # Calcular acumulado geral
    nfs_por_dia['NFs_Acumuladas_Geral'] = nfs_por_dia['NFs_Dia'].cumsum()
    
    # Calcular NFs por marca por dia
    nfs_por_marca_dia = df_unicas.groupby(['Dt Emis NF', 'Marca'])['Nota Fiscal'].nunique().reset_index()
    nfs_por_marca_dia.columns = ['Data', 'Marca', 'NFs_Dia_Marca']
    
    # Calcular acumulado por marca
    df_marca_final = []
    for marca in nfs_por_marca_dia['Marca'].unique():
        dados_marca = nfs_por_marca_dia[nfs_por_marca_dia['Marca'] == marca].copy()
        dados_marca = dados_marca.sort_values('Data')
        dados_marca['NFs_Acumuladas_Por_Marca'] = dados_marca['NFs_Dia_Marca'].cumsum()
        df_marca_final.append(dados_marca[['Data', 'Marca', 'NFs_Acumuladas_Por_Marca']])
    
    # Combinar dados de todas as marcas
    if df_marca_final:
        df_marca_completo = pd.concat(df_marca_final, ignore_index=True)
        df_marca_completo = df_marca_completo.sort_values(['Data', 'Marca'])
    else:
        df_marca_completo = pd.DataFrame(columns=['Data', 'Marca', 'NFs_Acumuladas_Por_Marca'])
    
    return nfs_por_dia, df_marca_completo


# ============================================================================
# FUNÇÕES PARA DADOS DE DEVOLUÇÃO
# ============================================================================

COLUNAS_DEVOLUCAO = [
    'Marca', 'Razao Social', 'Estado', 'Ped Cliente', 'Receita',
    'Tipo Oper', 'Serie', 'Nota Fiscal', 'Dt Emis NF', 'Item',
    'Desc Item', 'Localização', 'Quantidade', 'Vl Net Livro', 'Nro Embarque'
]


def carregar_dados_devolucao(df_bruto=None, anonimizar=True):
    """
    Carrega dados de devolução.

    Com `df_bruto` (relatório de faturamento no formato original), processa
    esses dados. Sem ele, usa o arquivo de demonstração ou, se não existir, o
    relatório real deixado na pasta (veja configuracao.py).

    Returns:
        pd.DataFrame: DataFrame processado com dados de devolução
    """
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    arquivo_processado = os.path.join(current_dir, cfg.ARQUIVO_DEMO_FATURAMENTO)
    arquivo_original = os.path.join(current_dir, cfg.ARQUIVO_FATURAMENTO)
    
    # Tentar carregar arquivo processado
    if df_bruto is None and os.path.exists(arquivo_processado):
        print("⚡ Carregando dados de devolução (processados)...")
        
        # Carregar arquivo processado
        df_devolucao = pd.read_csv(
            arquivo_processado, 
            sep=';', 
            encoding='latin1',
            dtype={'Nota Fiscal': str, 'Nro Embarque': str}
        )
        
        # Converter data
        df_devolucao['Dt Emis NF'] = pd.to_datetime(df_devolucao['Dt Emis NF'], errors='coerce')
        
        # Filtrar apenas devoluções
        df_devolucao = df_devolucao[df_devolucao['Tipo Oper'] == 'DEVOLUÇÃO']
        df_devolucao = df_devolucao[df_devolucao['Localização'] != cfg.LOCALIZACAO_EXPORTACAO]
        df_devolucao = df_devolucao.dropna(subset=['Dt Emis NF'])
        
        print(f"✅ Devoluções carregadas: {len(df_devolucao):,} registros")
        return df_devolucao
    
    # Se não existe arquivo processado, processar original
    print("⚠️  Processando devoluções do arquivo original...")
    devolucao_path = arquivo_original
    
    # Carregar dados
    if df_bruto is not None:
        df_devolucao = df_bruto[COLUNAS_DEVOLUCAO].copy()
    else:
        df_devolucao = pd.read_csv(
            devolucao_path,
            sep=';',
            encoding='latin1',
            usecols=COLUNAS_DEVOLUCAO,
            dtype={'Nota Fiscal': str, 'Nro Embarque': str}
        )

    # Anonimizar dados de Item, Razão Social e Pedidos
    if anonimizar:
        df_devolucao = anonimizar_itens(df_devolucao)
        df_devolucao = anonimizar_razao_social(df_devolucao)
        df_devolucao = anonimizar_pedidos(df_devolucao)
    
    # Converter coluna Serie para string
    df_devolucao['Serie'] = df_devolucao['Serie'].astype(str)
    
    # Limpar e padronizar marcas
    if "Marca" in df_devolucao.columns:
        # Remover marcas indesejadas (as unidades já estão padronizadas no arquivo processado)
        df_devolucao = df_devolucao[~df_devolucao["Marca"].isin(cfg.MARCAS_EXCLUIDAS)]


    # Preencher valores nulos
    df_devolucao.fillna({
        "Ped Cliente": "Sem Pedido", 
        "Nro Embarque": "Sem Embarque",
    }, inplace=True)
    
    # Converter receita para boolean
    if "Receita" in df_devolucao.columns:
        df_devolucao["Receita"] = (
            df_devolucao["Receita"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map({"sim": True, "não": False, "nao": False})
            .astype(bool)
        )
    
    # Converter valores numéricos com robustez
    for col in ["Vl Net Livro", "Quantidade"]:
        if col in df_devolucao.columns:
            serie = df_devolucao[col].astype(str).str.strip()
            # Remover espaços e símbolos não numéricos, manter , . -
            serie = serie.str.replace(r"[^0-9,.-]", "", regex=True)
            # Se houver vírgula, assumir pt-BR: remover separador de milhar e trocar vírgula por ponto
            tem_virgula = serie.str.contains(",")
            serie = serie.mask(tem_virgula, serie.str.replace(".", "", regex=False))
            serie = serie.mask(tem_virgula, serie.str.replace(",", ".", regex=False))
            # Converter
            df_devolucao[col] = pd.to_numeric(serie, errors="coerce").fillna(0.0).abs()
    
    # Categorizar tipos de operação antes de filtrar
    mapeamento_tipo_oper = {codigo: 'DEVOLUÇÃO' for codigo in cfg.TIPOS_OPERACAO_DEVOLUCAO}
    df_devolucao['Tipo Oper'] = df_devolucao['Tipo Oper'].replace(mapeamento_tipo_oper)
    
    # Filtrar apenas devoluções
    devolucao_filtros = ['DEVOLUÇÃO']
    df_devolucao = df_devolucao[df_devolucao['Tipo Oper'].isin(devolucao_filtros)]
    
    # Remover registros de exportação
    df_devolucao = df_devolucao[df_devolucao['Localização'] != cfg.LOCALIZACAO_EXPORTACAO]
    
    # Converter coluna de data
    if 'Dt Emis NF' in df_devolucao.columns:
        df_devolucao['Dt Emis NF'] = para_data(df_devolucao['Dt Emis NF']).dt.normalize()
        df_devolucao = df_devolucao.dropna(subset=['Dt Emis NF'])
    
    return df_devolucao


def calcular_metricas_devolucao(df_devolucao):
    """
    Calcula métricas principais de devolução.
    
    Args:
        df_devolucao (pd.DataFrame): DataFrame de devolução
        
    Returns:
        dict: Dicionário com métricas calculadas
    """
    if len(df_devolucao) == 0:
        return {
            'total_devolucao': 0,
            'qtd_devolucao': 0,
            'media_devolucao': 0,
            'devolucao_por_marca': pd.Series(dtype=float)
        }
    
    total_devolucao = df_devolucao['Vl Net Livro'].sum()
    qtd_devolucao = df_devolucao['Quantidade'].sum()
    media_devolucao = df_devolucao['Vl Net Livro'].mean()
    devolucao_por_marca = df_devolucao.groupby('Marca')['Vl Net Livro'].sum().sort_values(ascending=False)
    
    return {
        'total_devolucao': total_devolucao,
        'qtd_devolucao': qtd_devolucao,
        'media_devolucao': media_devolucao,
        'devolucao_por_marca': devolucao_por_marca
    }


def obter_cores_devolucao():
    """
    Retorna dicionário com cores padronizadas para marcas em devolução.
    Cores otimizadas para melhor contraste e legibilidade.
    
    Returns:
        dict: Dicionário com cores por marca
    """
    # Mesmas cores de obter_cores_marca para manter a identidade de cada unidade
    return dict(obter_cores_marca())



