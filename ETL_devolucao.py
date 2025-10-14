"""
ETL para dados de Devolução
===========================

Este módulo contém todas as funções de ETL (Extract, Transform, Load) 
para processamento de dados de devolução.

Autor: Sistema de Relatórios CI
Data: 2025
"""

import pandas as pd
import os
import sys
from faker import Faker
import hashlib

# Inicializar Faker e dicionários de cache globais
_faker = Faker('pt_BR')
_cache_item = {}
_cache_desc = {}
_cache_razao_social = {}
_cache_pedido = {}

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
    
    return df

def carregar_dados_devolucao():
    """
    Carrega e processa os dados de devolução.
    Retorna DataFrame com dados de devolução processados.
    """
    try:
        # Obter caminho do arquivo de devolução
        current_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_devolucao = os.path.join(current_dir, 'ESFT0100.csv')
        
        print(f"DEBUG ETL_devolucao: Tentando carregar arquivo de: {caminho_devolucao}")
        print(f"DEBUG ETL_devolucao: Arquivo existe? {os.path.exists(caminho_devolucao)}")

        # Definir colunas necessárias para devolução
        colunas = [
            'Marca', 'Deposito', 'Razao Social', 'Estado', 'Ped Cliente', 'Receita',
            'Tipo Oper', 'Serie', 'Nota Fiscal', 'Dt Emis NF',
            'Item', 'Desc Item', 'Localização', 'Quantidade', 'Vl Net Livro', 'Nro Embarque', 'Canal Venda Cliente'
        ]
        
        # Carregar dados de devolução
        df_devolucao = pd.read_csv(caminho_devolucao, sep=';', encoding='latin1', usecols=colunas, dtype={'Nota Fiscal': str, 'Nro Embarque': str})
        print(f"DEBUG ETL_devolucao: Dados carregados. Total de registros: {len(df_devolucao)}")
        
        # Processar dados
        df_devolucao = processar_dados_devolucao(df_devolucao)
        print(f"DEBUG ETL_devolucao: Dados processados. Total de registros após processamento: {len(df_devolucao)}")
      
        return df_devolucao
        
    except Exception as e:
        print(f"ERRO ao carregar dados de devolução: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def processar_dados_devolucao(df_devolucao):
    """
    Processa e limpa os dados de devolução.
    """
    print(f"DEBUG processar_dados_devolucao: Iniciando processamento com {len(df_devolucao)} registros")
    
    # Anonimizar dados de Item, Razão Social e Pedidos
    df_devolucao = anonimizar_itens(df_devolucao)
    df_devolucao = anonimizar_razao_social(df_devolucao)
    df_devolucao = anonimizar_pedidos(df_devolucao)
    
    # Categorizar Tipo Oper antes de filtrar
    print(f"DEBUG: Tipos de operação únicos antes da categorização: {df_devolucao['Tipo Oper'].unique()}")
    mapeamento_tipo_oper = {
        '5 - Dev Venda': 'DEVOLUÇÃO',
        '21 - Dev Compra': 'DEVOLUÇÃO',
    }
    df_devolucao['Tipo Oper'] = df_devolucao['Tipo Oper'].replace(mapeamento_tipo_oper)
    print(f"DEBUG: Tipos de operação únicos após categorização: {df_devolucao['Tipo Oper'].unique()}")
    
    df_devolucao = df_devolucao[df_devolucao["Tipo Oper"]=="DEVOLUÇÃO"]
    print(f"DEBUG: Registros após filtrar DEVOLUÇÃO: {len(df_devolucao)}")
    
    # Limpar dados
    df_devolucao['Vl Net Livro'] = df_devolucao['Vl Net Livro'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
    df_devolucao['Vl Net Livro'] = df_devolucao['Vl Net Livro'].abs()
    df_devolucao = df_devolucao[df_devolucao["Marca"] != "?"]


    df_devolucao['Quantidade'] = df_devolucao['Quantidade'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
    df_devolucao['Quantidade'] = df_devolucao['Quantidade'].abs()
    
    
    # Processar coluna Deposito se existir
    if 'Deposito' in df_devolucao.columns:
        df_devolucao['Deposito'] = df_devolucao['Deposito'].str.upper()
        df_devolucao = df_devolucao[df_devolucao['Deposito'].isin(['CD', 'CI', 'DPA', 'DEV', 'MTK', 'APA'])]
    
    # Converter data no formato brasileiro (DD/MM/YY)
    df_devolucao['Dt Emis NF'] = pd.to_datetime(df_devolucao['Dt Emis NF'], format='%d/%m/%y', errors='coerce')

    # Padronizar e categorizar canais de venda
    if 'Canal Venda Cliente' in df_devolucao.columns:
        df_devolucao['Canal Venda Cliente'] = df_devolucao['Canal Venda Cliente'].fillna('N/A')
        
        # Mapeamento de canais específicos para categorias mais amplas
        mapeamento_canais = {
            # B2B ATACADO
            'ATACADISTA': 'B2B ATACADO',
            'DISTRIBUIDOR': 'B2B ATACADO',
            'DISTRIBUIDOR VAR': 'B2B ATACADO',
            
            # B2B VAREJO
            'FERRAGISTA': 'B2B VAREJO',
            'MATERIAL DE CONSTRUCAO': 'B2B VAREJO',
            'HOME CENTER': 'B2B VAREJO',
            'CHAVEIRO': 'B2B VAREJO',
            'VAREJO VIP': 'B2B VAREJO',
            
            # B2B PROFISSIONAL
            'INTEGRADOR': 'B2B PROFISSIONAL',
            'INTEGRADOR VAR': 'B2B PROFISSIONAL',
            'INSTALADOR': 'B2B PROFISSIONAL',
            'CONSTRUTORA': 'B2B PROFISSIONAL',
            'SEGURANCA ELETRONICA': 'B2B PROFISSIONAL',
            'PROTECAO A INCENDIO': 'B2B PROFISSIONAL',
            
            # B2C
            'CONSUMIDOR FINAL PJ': 'B2C',
            'CONSUMIDOR FINAL PF': 'B2C',
            'PESSOA FISICA': 'B2C',
            'CLIENTE FINAL': 'B2C',
            
            # E-COMMERCE
            'WEBSHOP': 'E-COMMERCE',
            
            # OEM
            'OEM': 'OEM',
            'VENDA DIRETA': 'OEM',
            
            # INTERCOMPANY
            'INTERCOMPANY/BRZ': 'VENDA INTERNA',
            
            # NOVOS CANAIS
            'NOVOS CANAIS': 'NOVOS CANAIS',
        }
        
        # Aplicar mapeamento
        df_devolucao['Canal Venda Cliente'] = df_devolucao['Canal Venda Cliente'].replace(mapeamento_canais)

    # Filtrar marcas indesejadas (as unidades já estão padronizadas no arquivo processado)
    if "Marca" in df_devolucao.columns:
        indesejadas = {"?", "MTK CD SP"}
        df_devolucao = df_devolucao[~df_devolucao["Marca"].isin(indesejadas)]
    

    # Preencher valores nulos
    df_devolucao.fillna({
        "Ped Cliente": "Sem Pedido", 
        "Nro Embarque": "Sem Embarque",
    }, inplace=True)
    
    print(f"DEBUG processar_dados_devolucao: Processamento concluído. Total final de registros: {len(df_devolucao)}")

    return df_devolucao

def exibir_cards_devolucao_por_marca_bruto(df_devolucao):
    """
    Agrupa o DataFrame por marca, calcula o total por marca e retorna um DataFrame
    com as colunas padronizadas ('Marca' e 'Valor') para evitar erros de leitura.
    
    Trata notas fiscais duplicadas consolidando os valores por NF antes do agrupamento por marca.

    Args:
        df_devolucao (pd.DataFrame): DataFrame de devolução.

    Returns:
        pd.DataFrame: DataFrame com colunas 'Marca' e 'Valor' (total por marca).
    """
    # Verifica se o DataFrame está vazio
    if df_devolucao.empty:
        print("AVISO: DataFrame de devolução está vazio. Retornando DataFrame vazio.")
        return pd.DataFrame(columns=['Marca', 'Valor'])
    
    # Verifica se as colunas necessárias existem
    if "Marca" not in df_devolucao.columns or "Vl Net Livro" not in df_devolucao.columns or "Nota Fiscal" not in df_devolucao.columns:
        print(f"AVISO: Colunas disponíveis no DataFrame: {list(df_devolucao.columns)}")
        return pd.DataFrame(columns=['Marca', 'Valor'])

    # Primeiro, consolidar notas fiscais duplicadas
    # Agrupa por Nota Fiscal e Marca, somando TODOS os valores dos itens da mesma NF
    df_consolidado = (
        df_devolucao.groupby(['Nota Fiscal', 'Marca'])['Vl Net Livro']
        .sum()  # Soma todos os itens da mesma NF
        .reset_index()
    )
    
    # Renomear a coluna para Valor_NF_NET
    df_consolidado = df_consolidado.rename(columns={"Vl Net Livro": "Valor_NF_NET"})
    
    # Remover duplicatas de Nota Fiscal
    df_consolidado = df_consolidado.drop_duplicates(subset=['Nota Fiscal'])
    
    # Agora agrupa por marca e soma o valor consolidado das NFs
    devolucao_por_marca = (
        df_consolidado.groupby(df_consolidado['Marca'].astype(str))['Valor_NF_NET']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    
    # Padroniza o nome da coluna de valor para 'Valor'
    devolucao_por_marca = devolucao_por_marca.rename(columns={"Valor_NF_NET": "Valor"})

    return devolucao_por_marca

