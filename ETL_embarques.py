import pandas as pd
from datetime import datetime
from faker import Faker
import hashlib
import os

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
    Anonimiza a coluna 'Nr Ped Cli' ou 'Ped Cliente' de forma consistente.
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
    
    # Verifica diferentes nomes de colunas de pedido
    if 'Nr Ped Cli' in df.columns:
        df['Nr Ped Cli'] = df['Nr Ped Cli'].apply(gerar_pedido_falso)
    if 'Ped Cliente' in df.columns:
        df['Ped Cliente'] = df['Ped Cliente'].apply(gerar_pedido_falso)
    
    return df

def etl_embarques():
    colunas = [
        'Estab',
        'Unid. Negócio',
        'Embarque',
        'Dt Embarque',
        'Status',
        'PARADOS',
        'Nr Ped Cli',
        'Vl Net',
        'Situação',
        'Desc Canal',
        'UF Cli'
    ]
    # Obter caminho do arquivo Excel na raiz do projeto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tentar carregar arquivo falso primeiro, se não existir, carregar o original
    arquivo_falso = os.path.join(current_dir, 'embarques_falsos.xlsx')
    arquivo_original = os.path.join(current_dir, 'AAB-PF - REPORT DIÁRIO FATURAMENTO 2025 - AAB.xlsx')
    
    if os.path.exists(arquivo_falso):
        print("⚡ Carregando embarques falsos (dados anonimizados)...")
        excel_path = arquivo_falso
    else:
        print("📂 Carregando embarques originais...")
        excel_path = arquivo_original
    
    embarques = pd.read_excel(
        excel_path,
        sheet_name="BASE ESGR0050 POTENCIAL", dtype={'Estab': str, 'Embarque': str, 'Nr Ped Cli': str}, usecols=colunas
    )
    
    # Anonimizar pedidos apenas se for arquivo original
    if excel_path == arquivo_original:
        embarques = anonimizar_pedidos(embarques)
    
    # ETL GERAL
    embarques = embarques.dropna(subset=['Estab'])
    embarques = embarques[embarques['Unid. Negócio'] != 'XXXXXXXXXXXX']
    embarques = embarques[embarques['UF Cli'] != 'EX']
    embarques['Dt Embarque'] = embarques['Dt Embarque'].dt.strftime('%d/%m/%Y')
    hoje_str = datetime.today().strftime('%d/%m/%Y')
    
    # Processar canais apenas se for arquivo original (arquivo falso já vem categorizado)
    if excel_path == arquivo_original and 'Desc Canal' in embarques.columns:
        embarques['Desc Canal'] = embarques['Desc Canal'].fillna('N/A')
        
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
        embarques['Desc Canal'] = embarques['Desc Canal'].replace(mapeamento_canais)
        
        # Filtrar canal VENDA INTERNA
        embarques = embarques[embarques['Desc Canal'] != 'VENDA INTERNA']
    
    # Padronizar marcas apenas se for arquivo original (arquivo falso já vem padronizado)
    # As unidades já estão padronizadas no arquivo fake
    """
    Processa o DataFrame embarques para obter o potencial disponível.

    Retorna:
        agrupado_quantidade: DataFrame com a quantidade de linhas por 'Unid. Negócio'
        agrupado_bu: DataFrame com o somatório do 'Vl Net' por 'Unid. Negócio'
        embarques_potencial: DataFrame filtrado apenas com os embarques potenciais
    """
    
    # Calcular embarques potenciais
    embarques_potencial, agrupado_quantidade, agrupado_bu_potencial = potencial_disponivel(embarques)

    return agrupado_quantidade, agrupado_bu_potencial, embarques_potencial, embarques, hoje_str


def potencial_disponivel(embarques):
    """
    Filtra os embarques cujo 'Status' está vazio e retorna:
    - embarques_potencial: DataFrame filtrado
    - agrupado_quantidade: DataFrame com a quantidade de linhas por 'Unid. Negócio'
    - agrupado_bu_potencial: DataFrame com o somatório do 'Vl Net' por 'Unid. Negócio'
    """
    embarques_potencial = embarques.copy()
    embarques_potencial['Status'] = embarques_potencial['Status'].fillna('')
    embarques_potencial = embarques_potencial[embarques_potencial['Status'] == '']
    agrupado_quantidade = embarques_potencial.groupby('Unid. Negócio').size().reset_index(name='Quantidade de Linhas')
    agrupado_bu_potencial = embarques_potencial.groupby('Unid. Negócio')['Vl Net'].sum().reset_index()
    return embarques_potencial, agrupado_quantidade, agrupado_bu_potencial

# Gerar um arquivo .csv com os dados de embarques
#embarques.to_csv('embarques.csv', index=False, sep=';')


def faturado_dia(embarques, hoje_str):
    """
    Filtra e retorna os embarques faturados do dia, agrupando quantidade e valor por 'Unid. Negócio'.

    Parâmetros:
        embarques: DataFrame dos embarques totais.
        hoje_str: string da data de hoje no formato '%d/%m/%Y'.

    Retorna:
        embarques_hoje: DataFrame dos embarques faturados do dia.
        agrupado_quantidade_faturado: DataFrame com quantidade por unidade de negócio.
        agrupado_bu_faturado: DataFrame com somatório de valor por unidade de negócio.
    """
    embarques_faturado = embarques.copy()
    embarques_faturado = embarques_faturado[embarques_faturado['Situação'] == 'NaN']
    # Filtrar os embarques do dia atual em 'Dt Embarque'
    embarques_hoje = embarques_faturado[embarques_faturado['Dt Embarque'] == hoje_str]
    agrupado_quantidade_faturado = embarques_hoje.groupby('Unid. Negócio').size().reset_index(name='Quantidade de Linhas')
    agrupado_bu_faturado = embarques_hoje.groupby('Unid. Negócio')['Vl Net'].sum().reset_index()
    return embarques_hoje, agrupado_quantidade_faturado, agrupado_bu_faturado


def calcular_potencial_faturamento(embarques, hoje_str):
    """
    Calcula o potencial de faturamento por marca baseado em:
    - Embarques potenciais (Status vazio)
    - Embarques faturados (Situação = 'NaN' e Dt Embarque = hoje)

    Parâmetros:
        embarques: DataFrame de todos os embarques
        hoje_str: data de hoje como string para filtro

    Retorna:
        DataFrame com potencial de faturamento e quantidade de embarques por Unid. Negócio
    """
    # Usa as funções já criadas
    # Potenciais
    embarques_potencial, agrupado_quantidade_potencial, agrupado_bu_potencial = potencial_disponivel(embarques)
    # Faturados do dia
    embarques_hoje, agrupado_quantidade_faturado, agrupado_bu_faturado = faturado_dia(embarques, hoje_str)

    # Lista de todas unidades de negócio
    unidades_negocio = pd.Series(list(set(list(agrupado_bu_potencial['Unid. Negócio']) + list(agrupado_bu_faturado['Unid. Negócio']))))

    # Inicia DataFrame base
    potencial_df = pd.DataFrame({'Unid. Negócio': unidades_negocio})
    potencial_df = potencial_df.sort_values('Unid. Negócio').reset_index(drop=True)

    # Junta resultados de potencial
    potencial_df = potencial_df.merge(
        agrupado_bu_potencial.rename(columns={'Vl Net': 'Embarques_Potencial'}),
        on='Unid. Negócio', how='left'
    )
    potencial_df = potencial_df.merge(
        agrupado_quantidade_potencial.rename(columns={'Quantidade de Linhas': 'Qtd_Embarques_Potencial'}),
        on='Unid. Negócio', how='left'
    )

    # Junta resultados de faturado
    potencial_df = potencial_df.merge(
        agrupado_bu_faturado.rename(columns={'Vl Net': 'Embarques_Faturado'}),
        on='Unid. Negócio', how='left'
    )
    potencial_df = potencial_df.merge(
        agrupado_quantidade_faturado.rename(columns={'Quantidade de Linhas': 'Qtd_Embarques_Faturado'}),
        on='Unid. Negócio', how='left'
    )

    # Preenche nulos com 0
    for col in ['Embarques_Potencial', 'Qtd_Embarques_Potencial', 'Embarques_Faturado', 'Qtd_Embarques_Faturado']:
        potencial_df[col] = potencial_df[col].fillna(0)

    # Calcula totais
    potencial_df['Potencial_Total'] = potencial_df['Embarques_Potencial'] + potencial_df['Embarques_Faturado']
    potencial_df['Qtd_Embarques_Total'] = potencial_df['Qtd_Embarques_Potencial'] + potencial_df['Qtd_Embarques_Faturado']

    # Ordena pelo potencial total decrescente
    potencial_df = potencial_df.sort_values('Potencial_Total', ascending=False).reset_index(drop=True)

    return potencial_df

