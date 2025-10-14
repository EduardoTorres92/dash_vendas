import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import importlib.util
import json

# Adicionar o diretório atual ao path (onde estão os arquivos ETL)
current_dir = os.path.dirname(os.path.abspath(__file__))
etl_path = current_dir  # Os arquivos ETL estão no mesmo diretório
if etl_path not in sys.path:
    sys.path.insert(0, etl_path)

### ETL Imports

# Importar ETL_faturamento
spec_faturamento = importlib.util.spec_from_file_location("ETL_faturamento", os.path.join(etl_path, "ETL_faturamento.py"))
etl_faturamento = importlib.util.module_from_spec(spec_faturamento)
spec_faturamento.loader.exec_module(etl_faturamento)

# Importar ETL_devolucao
spec_devolucao = importlib.util.spec_from_file_location("ETL_devolucao", os.path.join(etl_path, "ETL_devolucao.py"))
etl_devolucao = importlib.util.module_from_spec(spec_devolucao)
spec_devolucao.loader.exec_module(etl_devolucao)

# Importar ETL_embarques
spec_embarques = importlib.util.spec_from_file_location("ETL_embarques", os.path.join(etl_path, "ETL_embarques.py"))
etl_embarques = importlib.util.module_from_spec(spec_embarques)
spec_embarques.loader.exec_module(etl_embarques)


    

st.set_page_config(
    page_title="Faturamento",
    page_icon="💰",
    layout="wide"
)

# OTIMIZAÇÃO: Sistema de cache para dados já carregados
@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_dados_com_cache():
    """
    Carrega dados com cache para evitar recarregamentos desnecessários
    """
    faturado = etl_faturamento.carregar_dados_faturamento()
    df_devolucao_card = etl_devolucao.carregar_dados_devolucao()
    cores_marca = etl_faturamento.obter_cores_marca()
    return faturado, df_devolucao_card, cores_marca

# Carregar dados usando ETL centralizado com cache
faturado, df_devolucao_card, cores_marca = carregar_dados_com_cache()

# Filtrar marcas indesejadas que podem ter passado pelo processamento
marcas_indesejadas_finais = ['?', 'MTK CD SP']
if 'Marca' in faturado.columns:
    faturado = faturado[~faturado['Marca'].isin(marcas_indesejadas_finais)]
if 'Marca' in df_devolucao_card.columns and len(df_devolucao_card) > 0:
    df_devolucao_card = df_devolucao_card[~df_devolucao_card['Marca'].isin(marcas_indesejadas_finais)]

# Criar cópia dos dados completos ANTES dos filtros (para análise mensal)
faturado_completo = faturado.copy()

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

def formatar_titulo_marcas(titulo_base, marcas_selecionadas, marcas_disponiveis):
    """
    Formata o título baseado nas marcas selecionadas
    """
    if not marcas_selecionadas or len(marcas_selecionadas) == len(marcas_disponiveis):
        return titulo_base
    elif len(marcas_selecionadas) == 1:
        return f"{titulo_base} - {marcas_selecionadas[0]}"
    else:
        marcas_str = ", ".join(marcas_selecionadas)
        return f"{titulo_base} - {marcas_str}"


# Filtro de Região

# Verificar se a coluna Estado existe antes de usar
if 'Estado' in faturado.columns:
    # Adicionar coluna de região baseada no estado
    faturado['Região'] = faturado['Estado'].apply(etl_faturamento.obter_regiao_por_estado)
else:
    st.error("Coluna 'Estado' não encontrada no DataFrame")

# Garantir que a coluna de data está no formato datetime e filtrar por mês selecionado no menu lateral
if 'Dt Emis NF' in faturado.columns and len(faturado) > 0:
    # Converter para datetime e normalizar
    faturado['Dt Emis NF'] = pd.to_datetime(faturado['Dt Emis NF'], format='%d/%m/%y', errors='coerce').dt.normalize()
    faturado = faturado.dropna(subset=['Dt Emis NF'])

    # Padronizar a coluna de data nas devoluções também, se existir
    if 'Dt Emis NF' in df_devolucao_card.columns and len(df_devolucao_card) > 0:
        df_devolucao_card['Dt Emis NF'] = pd.to_datetime(df_devolucao_card['Dt Emis NF'], format='%d/%m/%y', errors='coerce').dt.normalize()
        df_devolucao_card = df_devolucao_card.dropna(subset=['Dt Emis NF'])

    if len(faturado) > 0:
        # Obter meses únicos disponíveis
        meses_disponiveis = faturado['Dt Emis NF'].dt.to_period('M').unique()
        meses_disponiveis = sorted(meses_disponiveis)

        # Criar lista de opções para o selectbox
        opcoes_meses = []
        for mes_periodo in meses_disponiveis:
            ano = mes_periodo.year
            mes_num = mes_periodo.month
            mes_nome = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }[mes_num]
            opcoes_meses.append(f"{mes_nome}/{ano}")

        # Seletor de filtro de data no menu lateral
        with st.sidebar:
            # Primeiro selecionar o tipo de filtro
            tipo_filtro = st.selectbox(
                "Tipo de Filtro:",
                options=["Por Mês", "Todos os Dados"],
                index=0,
                help="Escolha como deseja filtrar os dados"
            )
            
            mes_selecionado = None
            
            if tipo_filtro == "Por Mês":
                mes_selecionado = st.selectbox(
                    "Selecione o Mês:",
                    options=opcoes_meses,
                    index=len(opcoes_meses)-1 if opcoes_meses else 0,
                    help="Selecione o mês para filtrar os dados"
                )
            
            # Separador visual
            st.markdown("---")
            
            # Seletor de marcas (multi-select)
            marcas_disponiveis = sorted(faturado['Marca'].dropna().unique())
            marcas_selecionadas = st.multiselect(
                "Selecione as Marcas:",
                options=marcas_disponiveis,
                default=marcas_disponiveis,  # Por padrão, todas as marcas são selecionadas
                help="Escolha uma ou mais marcas para filtrar os dados"
            )
            
            # Separador visual
            st.markdown("---")
            
            # Filtro de Dia (menu lateral) - depende do mês selecionado
            st.subheader("📅 Filtro de Dia")
            
            # Seletor de dia (1-31)
            dia_selecionado = st.selectbox(
                "Selecionar Dia:",
                options=["Todos os dias"] + [f"Dia {i}" for i in range(1, 32)],
                index=0,
                help="Selecione um dia específico do mês para filtrar os dados"
            )
            
            # Separador visual
            st.markdown("---")
            
            # Filtro de Receita (radiobox)
            filtro_receita = st.radio(
                "Tipo de Receita:",
                options=["Ambas", "Sim", "Não"],
                index=0,  # "Ambas" como padrão
                help="Sim = Receitas normais (1-Receita, 20-Receita Revenda) | Não = Brindes/Transferências (9-Brindes, 15-Transferencia) | Ambas = Todos os tipos"
            )

        # Aplicar filtro conforme o tipo selecionado
        if tipo_filtro == "Por Mês" and mes_selecionado:
            # Extrair mês e ano da seleção
            mes_nome, ano_str = mes_selecionado.split('/')
            ano = int(ano_str)
            mes_num = {
                'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
                'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
                'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
            }[mes_nome]

            # Calcular primeiro e último dia do mês
            import datetime
            data_inicio = datetime.date(ano, mes_num, 1)
            if mes_num == 12:
                data_fim = datetime.date(ano + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                data_fim = datetime.date(ano, mes_num + 1, 1) - datetime.timedelta(days=1)

            # Aplicar filtro de data para o mês selecionado
            faturado = faturado[
                (faturado['Dt Emis NF'].dt.date >= data_inicio) &
                (faturado['Dt Emis NF'].dt.date <= data_fim)
            ]

            # Aplicar o mesmo filtro de data para as devoluções, se existir a coluna padronizada
            if 'Dt Emis NF' in df_devolucao_card.columns and len(df_devolucao_card) > 0:
                df_devolucao_card = df_devolucao_card[
                    (df_devolucao_card['Dt Emis NF'].dt.date >= data_inicio) &
                    (df_devolucao_card['Dt Emis NF'].dt.date <= data_fim)
                ]
                
        # Se tipo_filtro == "Todos os Dados", não aplica nenhum filtro
        
        # Aplicar filtro de marcas se marcas específicas foram selecionadas
        if marcas_selecionadas and len(marcas_selecionadas) < len(marcas_disponiveis):
            faturado = faturado[faturado['Marca'].isin(marcas_selecionadas)]
            # Aplicar o mesmo filtro de marcas para as devoluções, se existir a coluna padronizada
            if 'Marca' in df_devolucao_card.columns and len(df_devolucao_card) > 0:
                df_devolucao_card = df_devolucao_card[df_devolucao_card['Marca'].isin(marcas_selecionadas)]
        
        # Aplicar filtro de dia se selecionado
        if dia_selecionado and dia_selecionado != "Todos os dias":
            # Extrair o número do dia (ex: "Dia 3" -> 3)
            numero_dia = int(dia_selecionado.split()[1])
            
            # Aplicar filtro de dia
            faturado = faturado[faturado['Dt Emis NF'].dt.day == numero_dia]
            
            # Aplicar o mesmo filtro para as devoluções
            if 'Dt Emis NF' in df_devolucao_card.columns and len(df_devolucao_card) > 0:
                df_devolucao_card = df_devolucao_card[df_devolucao_card['Dt Emis NF'].dt.day == numero_dia]
        
        # Aplicar filtro de Receita globalmente usando as funções específicas do ETL
        if filtro_receita == "Sim":
            # Apenas receitas normais (Receita Sim): "1 - Receita", "20 - Receita Revenda"
            faturado = etl_faturamento.filtrar_receita_sim(faturado)
        elif filtro_receita == "Não":
            # Apenas brindes e transferências (Receita Não): "9 - Brindes / Bonificações", "15 - Transferencia"
            faturado = etl_faturamento.filtrar_receita_nao(faturado)
        # Se filtro_receita == "Ambas", não aplica filtro adicional
                
    else:
        st.warning("⚠️ Nenhum dado válido encontrado")
else:
    st.warning("Coluna 'Dt Emis NF' não encontrada no dataset")

faturamento_diario = faturado.groupby("Dt Emis NF", as_index=False)[
    "Vl Net Livro"
].sum()

# 🪄 Formatar valores para tooltip e texto no gráfico
faturamento_diario["vl_formatado"] = faturamento_diario["Vl Net Livro"].apply(
    lambda x: formatar_valor_seguro(x, "currency")
)

faturamento_por_marca = etl_faturamento.exibir_cards_faturamento_por_marca_bruto(faturado)



# Calcular cut-off baseado no tipo de filtro - OTIMIZADO
cut_off_por_marca = {}
cut_off_inicial_por_marca = {}  # Cut-off do mês anterior (a ser adicionado)
cut_off_total = 0
cut_off_inicial_total = 0

if 'tipo_filtro' in locals():
    if tipo_filtro == "Por Mês" and 'mes_selecionado' in locals() and mes_selecionado:
        mes_nome, ano_str = mes_selecionado.split('/')
        
        # Calcular mês anterior para obter cut-off inicial
        mes_num = {
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
            'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
            'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        }[mes_nome]
        
        # Calcular mês anterior
        if mes_num == 1:
            mes_anterior_num = 12
            ano_anterior = int(ano_str) - 1
        else:
            mes_anterior_num = mes_num - 1
            ano_anterior = int(ano_str)
            
        # Nome do mês anterior
        mes_anterior_nome = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }[mes_anterior_num]
        
        # OTIMIZAÇÃO: Calcular cut-offs de uma vez para todas as marcas
        # Criar cache de cut-offs para evitar chamadas repetitivas
        cut_off_cache_atual = {}
        cut_off_cache_anterior = {}
        
        # Pre-calcular cut-offs para todas as marcas de uma vez
        # Agora as marcas já estão padronizadas (MARCA A, MARCA B, etc.)
        for marca in faturamento_por_marca['Marca']:
            # Cut-off do mês atual (a ser subtraído)
            cut_off_valor = etl_faturamento.obter_cut_off_por_marca_mes(marca, mes_nome)
            cut_off_cache_atual[marca] = cut_off_valor
            
            # Cut-off do mês anterior (a ser adicionado como receita)
            cut_off_inicial_valor = etl_faturamento.obter_cut_off_por_marca_mes(marca, mes_anterior_nome)
            cut_off_cache_anterior[marca] = cut_off_inicial_valor
        
        # Aplicar valores do cache
        cut_off_por_marca = cut_off_cache_atual
        cut_off_inicial_por_marca = cut_off_cache_anterior
        cut_off_total = sum(cut_off_cache_atual.values())
        cut_off_inicial_total = sum(cut_off_cache_anterior.values())

# Carregar dados de devolução
devolucao_por_marca = etl_devolucao.exibir_cards_devolucao_por_marca_bruto(df_devolucao_card)

# Criar dicionários para facilitar o cálculo
faturamento_dict = dict(zip(faturamento_por_marca['Marca'], faturamento_por_marca['Valor']))
devolucao_dict = dict(zip(devolucao_por_marca['Marca'], devolucao_por_marca['Valor']))

# Calcular faturamento líquido para cada marca
faturamento_liquido_por_marca = {}
total_faturamento_liquido = 0

for marca in faturamento_por_marca['Marca']:
    faturamento_bruto = faturamento_dict.get(marca, 0)
    devolucao = devolucao_dict.get(marca, 0)
    cut_off = cut_off_por_marca.get(marca, 0)
    cut_off_inicial = cut_off_inicial_por_marca.get(marca, 0)
    
    # Faturamento líquido = Bruto + Cut-off Inicial - Devoluções - Cut-off Atual
    faturamento_liquido = faturamento_bruto + cut_off_inicial - devolucao - cut_off
    faturamento_liquido_por_marca[marca] = faturamento_liquido
    total_faturamento_liquido += faturamento_liquido

# Calcular total geral para percentuais
total_geral = sum(faturamento_dict.values())

@st.cache_data(ttl=300)  # Cache por 5 minutos
def calcular_variacoes_mes_anterior_todas_marcas(faturamento_por_marca, tipo_filtro, mes_selecionado):
    """
    Calcula a variação percentual para todas as marcas de uma vez, evitando recarregar dados.
    OTIMIZADO: Usa cache para evitar recálculos desnecessários.
    
    Args:
        faturamento_por_marca (dict): Dicionário com faturamento por marca
        tipo_filtro (str): Tipo de filtro aplicado
        mes_selecionado (str): Mês selecionado no formato "Nome/Ano"
        
    Returns:
        dict: Dicionário com variação percentual para cada marca
    """
    variacoes = {}
    
    try:
        if tipo_filtro != "Por Mês" or not mes_selecionado:
            # Para "Todos os Dados", retornar 0 para todas as marcas
            return {marca: 0.0 for marca in faturamento_por_marca['Marca']}
        
        # OTIMIZAÇÃO: Usar dados já carregados com cache
        faturado_completo, _, _ = carregar_dados_com_cache()
        
        if len(faturado_completo) == 0:
            return {marca: 0.0 for marca in faturamento_por_marca['Marca']}
            
        # Converter datas apenas uma vez
        faturado_completo['Dt Emis NF'] = pd.to_datetime(faturado_completo['Dt Emis NF'], format='%d/%m/%y', errors='coerce').dt.normalize()
        faturado_completo = faturado_completo.dropna(subset=['Dt Emis NF'])
        
        # Determinar mês anterior
        mes_nome, ano_str = mes_selecionado.split('/')
        ano = int(ano_str)
        mes_num = {
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
            'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
            'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        }[mes_nome]
        
        # Calcular mês anterior
        if mes_num == 1:
            mes_anterior = 12
            ano_anterior = ano - 1
        else:
            mes_anterior = mes_num - 1
            ano_anterior = ano
            
        # Calcular primeiro e último dia do mês anterior
        import datetime
        data_inicio_anterior = datetime.date(ano_anterior, mes_anterior, 1)
        if mes_anterior == 12:
            data_fim_anterior = datetime.date(ano_anterior + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            data_fim_anterior = datetime.date(ano_anterior, mes_anterior + 1, 1) - datetime.timedelta(days=1)
        
        # Filtrar dados do mês anterior para todas as marcas de uma vez
        faturado_mes_anterior = faturado_completo[
            (faturado_completo['Dt Emis NF'].dt.date >= data_inicio_anterior) &
            (faturado_completo['Dt Emis NF'].dt.date <= data_fim_anterior)
        ]
        
        if len(faturado_mes_anterior) == 0:
            return {marca: 0.0 for marca in faturamento_por_marca['Marca']}
        
        # Consolidar notas fiscais duplicadas para o mês anterior
        df_consolidado_anterior = (
            faturado_mes_anterior.groupby(['Nota Fiscal', 'Marca'])['Vl Net Livro']
            .sum()
            .reset_index()
        )
        
        # Calcular faturamento do mês anterior por marca
        faturamento_mes_anterior_por_marca = df_consolidado_anterior.groupby('Marca')['Vl Net Livro'].sum()
        
        # Calcular variação para cada marca
        for marca in faturamento_por_marca['Marca']:
            valor_atual = faturamento_por_marca[faturamento_por_marca['Marca'] == marca]['Valor'].iloc[0]
            faturamento_mes_anterior = faturamento_mes_anterior_por_marca.get(marca, 0)
            
            if faturamento_mes_anterior > 0:
                variacao = ((valor_atual - faturamento_mes_anterior) / faturamento_mes_anterior) * 100
                variacoes[marca] = round(variacao, 1)
            else:
                # Se não havia faturamento no mês anterior, considerar crescimento de 100%
                variacoes[marca] = 100.0 if valor_atual > 0 else 0.0
                
    except Exception as e:
        # Em caso de erro, retornar 0 para todas as marcas
        variacoes = {marca: 0.0 for marca in faturamento_por_marca['Marca']}
    
    return variacoes

def calcular_variacao_mes_anterior(marca_atual, valor_atual, tipo_filtro, mes_selecionado):
    """
    Função mantida para compatibilidade, mas agora usa cache quando possível.
    """
    # Esta função agora é usada apenas como fallback
    # A versão otimizada é calcular_variacoes_mes_anterior_todas_marcas
    return 0.0

# Mostrar informações do filtro aplicado
titulo_principal = formatar_titulo_marcas("💰 Faturamento Líquido por Marca", marcas_selecionadas, marcas_disponiveis)
st.markdown(f"### {titulo_principal}")

# OTIMIZAÇÃO: Calcular todas as variações de uma vez
variacoes_todas_marcas = calcular_variacoes_mes_anterior_todas_marcas(faturamento_por_marca, tipo_filtro, mes_selecionado)

# Exibir cards de faturamento líquido com detalhes - OTIMIZADO
colunas = st.columns(len(faturamento_liquido_por_marca))
for idx, (marca, valor_liquido) in enumerate(faturamento_liquido_por_marca.items()):
    col = colunas[idx]
    
    # Valores para o card
    faturamento_bruto = faturamento_dict.get(marca, 0)
    devolucao = devolucao_dict.get(marca, 0)
    cut_off = cut_off_por_marca.get(marca, 0)
    cut_off_inicial = cut_off_inicial_por_marca.get(marca, 0)
    
    # Formatação dos valores
    faturamento_liquido_formatado = formatar_valor_seguro(valor_liquido, "currency")
    valor_formatado = formatar_valor_seguro(faturamento_bruto, "currency")
    cut_off_formatado = formatar_valor_seguro(cut_off, "currency")
    cut_off_inicial_formatado = formatar_valor_seguro(cut_off_inicial, "currency")
    devolucao_formatado = formatar_valor_seguro(devolucao, "currency")
    
    # Calcular percentual do faturamento bruto
    percentual_atual = (faturamento_bruto / total_geral * 100) if total_geral > 0 else 0
    
    # OTIMIZAÇÃO: Usar variação pré-calculada
    variacao_percentual = variacoes_todas_marcas.get(marca, 0.0)
    
    # Determinar cor da variação
    cor_variacao = "#28a745" if variacao_percentual >= 0 else "#dc3545"
    simbolo_variacao = "↗️" if variacao_percentual >= 0 else "↘️"
    
    # Cor da marca
    cor_marca = cores_marca.get(marca.upper(), "#6c757d")
    
    with col:
        st.markdown(f"""
        <div style="
            background: #B0BFCC; 
            border-radius: 15px; 
            padding: 20px 15px; 
            margin-bottom: 15px; 
            box-shadow: 0 6px 20px rgba(0,0,0,0.1); 
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        ">
            <div style="font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;">
                {marca}
            </div>
            <div style="font-size: 24px; font-weight: bold; color: white; margin-bottom: 8px;">
                {faturamento_liquido_formatado}
            </div>
            <div style="font-size: 12px; color: {cor_variacao}; font-weight: bold; margin-bottom: 15px;">
                {simbolo_variacao} {variacao_percentual:+.1f}% vs mês anterior
            </div>
            <div style="
                background: rgba(255,255,255,0.15); 
                border-radius: 8px; 
                padding: 10px; 
                font-size: 11px; 
                color: white;
                line-height: 1.4;
            ">
                <div style="margin-bottom: 5px;">
                    <strong>Bruto:</strong> {valor_formatado} ({percentual_atual:.1f}%)
                </div>
                <div style="margin-bottom: 3px;">
                    <strong>Cut-off Inicial:</strong> {cut_off_inicial_formatado}
                </div>
                <div style="margin-bottom: 3px;">
                    <strong>Cut-off:</strong> {cut_off_formatado}
                </div>
                <div>
                    <strong>Devoluções:</strong> {devolucao_formatado}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)




# Primeiro grupo de abas - Análises
tab_unidade_negocio, tab_canal_venda, tab_ontem = st.tabs(["📊 Análise por Unidade de Negócio", "🛒 Análise por Canal de Venda por Marca", "📅 Relatório do Dia Anterior por Marca"])

with tab_unidade_negocio:
    # Análise por Unidade de Negócio
    titulo_unidade = formatar_titulo_marcas("📊 Análise por Unidade de Negócio", marcas_selecionadas, marcas_disponiveis)
    st.subheader(titulo_unidade)
    
    analise_unidade_negocio = etl_faturamento.analisar_faturamento_por_unidade_negocio(faturado)

    # Formatar valores para exibição
    analise_unidade_negocio['VALOR_NET_Formatado'] = analise_unidade_negocio['VALOR_NET'].apply(
        lambda x: formatar_valor_seguro(x, "currency")
    )
    analise_unidade_negocio['Ticket_Medio_Formatado'] = analise_unidade_negocio['Ticket_Medio'].apply(
        lambda x: formatar_valor_seguro(x, "currency")
    )

    # Criar DataFrame para exibição com colunas formatadas
    df_exibicao = analise_unidade_negocio[['Unidade_de_Negocio', 'VALOR_NET_Formatado', 'QTD_NFs', 'Ticket_Medio_Formatado']].copy()
    df_exibicao.columns = ['Unidade de Negócio', 'VALOR NET', 'QTD. NFs', 'Ticket médio']

    # Exibir tabela formatada
    st.dataframe(
        df_exibicao,
        use_container_width=True,
        hide_index=True
    )

with tab_canal_venda:
    # Análise por Canal de Venda por Marca
    titulo_canal = formatar_titulo_marcas("🛒 Análise por Canal de Venda por Marca", marcas_selecionadas, marcas_disponiveis)
    st.subheader(titulo_canal)
    
    analise_canal_por_marca = etl_faturamento.analisar_canal_venda_por_marca(faturado)

    # Criar abas para cada marca
    if analise_canal_por_marca:
        # Obter cores das marcas para destaque
        cores_marca = etl_faturamento.obter_cores_marca()
        
        # Criar lista de abas
        tabs = st.tabs([f"🏷️ {marca}" for marca in analise_canal_por_marca.keys()])
        
        for idx, (marca, df_marca) in enumerate(analise_canal_por_marca.items()):
            with tabs[idx]:
                # Formatar valores para exibição
                df_marca['VALOR_NET_Formatado'] = df_marca['VALOR_NET'].apply(
                    lambda x: formatar_valor_seguro(x, "currency")
                )
                df_marca['Ticket_Medio_Formatado'] = df_marca['Ticket_Medio'].apply(
                    lambda x: formatar_valor_seguro(x, "currency")
                )
                
                # Criar DataFrame para exibição com colunas formatadas que corresponde à imagem
                df_exibicao = df_marca[['Unidade_Negocio', 'VALOR_NET_Formatado', 'QTD_NFs', 'Ticket_Medio_Formatado']].copy()
                df_exibicao.columns = ['Unidade de Negócio', 'VALOR NET', 'QTD. NFs', 'Ticket médio']
                
                # Exibir tabela formatada
                st.dataframe(
                    df_exibicao,
                    use_container_width=True,
                    hide_index=True
                )
with tab_ontem:
    # 📅 RELATÓRIO DO DIA ANTERIOR POR MARCA
    titulo_ontem = formatar_titulo_marcas("📅 Relatório do Dia Anterior por Marca", marcas_selecionadas, marcas_disponiveis)
    st.header(titulo_ontem)

    # Calcular data do dia anterior
    import datetime
    hoje = datetime.date.today()
    dia_anterior = hoje - datetime.timedelta(days=1)

    # Converter coluna de data para datetime se ainda não estiver
    if 'Dt Emis NF' in faturado.columns:
        faturado['Dt Emis NF'] = pd.to_datetime(faturado['Dt Emis NF'], errors='coerce')
        
        # Filtrar dados do dia anterior
        faturado_dia_anterior = faturado[faturado['Dt Emis NF'].dt.date == dia_anterior]
        
        if len(faturado_dia_anterior) > 0:
            # Agrupar por marca e somar quantidade de itens
            relatorio_dia_anterior = faturado_dia_anterior.groupby('Marca').agg({
                'Quantidade': 'sum',
                'Vl Net Livro': 'sum',
                'Item': 'nunique',  # Contar itens únicos (SKUs)
                'Nota Fiscal': 'nunique'  # Contar notas fiscais únicas
            }).reset_index()
            
            # Renomear colunas
            relatorio_dia_anterior.columns = ['Marca', 'Qtd Itens', 'Valor Total', 'SKUs Únicos', 'NFs Únicas']
            
            # Ordenar por quantidade de itens (decrescente)
            relatorio_dia_anterior = relatorio_dia_anterior.sort_values('Qtd Itens', ascending=False)
            
            # Formatar valores
            relatorio_dia_anterior['Qtd Itens'] = relatorio_dia_anterior['Qtd Itens'].apply(
                lambda x: formatar_valor_seguro(x, "number")
            )
            relatorio_dia_anterior['Valor Total'] = relatorio_dia_anterior['Valor Total'].apply(
                lambda x: formatar_valor_seguro(x, "currency")
            )
            relatorio_dia_anterior['SKUs Únicos'] = relatorio_dia_anterior['SKUs Únicos'].apply(
                lambda x: formatar_valor_seguro(x, "number")
            )
            relatorio_dia_anterior['NFs Únicas'] = relatorio_dia_anterior['NFs Únicas'].apply(
                lambda x: formatar_valor_seguro(x, "number")
            )
            
            # Exibir informações do dia
            col_info, col_total, col_valor = st.columns(3)
            
            with col_info:
                st.info(f"📊 **Data:** {dia_anterior.strftime('%d/%m/%Y')} ({dia_anterior.strftime('%A')})")
            
            with col_total:
                total_itens_dia = faturado_dia_anterior['Quantidade'].sum()
                total_valor_dia = faturado_dia_anterior['Vl Net Livro'].sum()
                st.metric("📦 Total de Itens", formatar_valor_seguro(total_itens_dia, "number"))
                
            with col_valor:
                st.metric("💰 Valor Total", formatar_valor_seguro(total_valor_dia, "currency"))
            
            # Criar abas para diferentes análises
            tab_resumo_marca, tab_canal_venda = st.tabs(["📋 Resumo por Marca", "🛒 Análise por Canal de Venda"])
            
            with tab_resumo_marca:
                st.subheader("📋 Detalhamento por Marca")
                
                # Usar as funções do ETL para análise de receita
                if 'Tipo Oper' in faturado_dia_anterior.columns:
                    # Usar função do ETL para análise completa
                    relatorio_completo = etl_faturamento.analisar_receita_completa_por_marca(faturado_dia_anterior)
                    
                    if not relatorio_completo.empty:
                        # Criar cópia para formatação
                        relatorio_formatado = relatorio_completo.copy()
                        
                        # Formatar valores
                        relatorio_formatado['Receita Sim'] = relatorio_formatado['Receita Sim'].apply(
                            lambda x: formatar_valor_seguro(x, "currency")
                        )
                        relatorio_formatado['Receita Não'] = relatorio_formatado['Receita Não'].apply(
                            lambda x: formatar_valor_seguro(x, "currency")
                        )
                        relatorio_formatado['QTD. NFs'] = relatorio_formatado['QTD. NFs'].apply(
                            lambda x: formatar_valor_seguro(x, "number")
                        )
                        relatorio_formatado['QTD. NFs (NÃO)'] = relatorio_formatado['QTD. NFs (NÃO)'].apply(
                            lambda x: formatar_valor_seguro(x, "number")
                        )
                        
                        # Adicionar linha de total usando as funções específicas do ETL
                        df_receita_sim = etl_faturamento.filtrar_receita_sim(faturado_dia_anterior)
                        df_receita_nao = etl_faturamento.filtrar_receita_nao(faturado_dia_anterior)
                        
                        # Calcular totais usando as funções específicas do ETL
                        total_receita_sim = df_receita_sim['Vl Net Livro'].sum() if not df_receita_sim.empty else 0
                        total_receita_nao = df_receita_nao['Vl Net Livro'].sum() if not df_receita_nao.empty else 0
                        total_nfs_sim = df_receita_sim['Nota Fiscal'].nunique() if not df_receita_sim.empty else 0
                        total_nfs_nao = df_receita_nao['Nota Fiscal'].nunique() if not df_receita_nao.empty else 0
                        
                        linha_total = pd.DataFrame({
                            'Marca': ['TOTAL'],
                            'Receita Sim': [formatar_valor_seguro(total_receita_sim, "currency")],
                            'QTD. NFs': [formatar_valor_seguro(total_nfs_sim, "number")],
                            'Receita Não': [formatar_valor_seguro(total_receita_nao, "currency")],
                            'QTD. NFs (NÃO)': [formatar_valor_seguro(total_nfs_nao, "number")]
                        })
                        
                        # Combinar dados com linha de total
                        relatorio_final = pd.concat([relatorio_formatado, linha_total], ignore_index=True)
                        
                        # Exibir tabela formatada
                        st.dataframe(
                            relatorio_final,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("ℹ️ Nenhum dado de receita encontrado para o dia anterior")
                    
                else:
                    # Fallback para estrutura original se não houver coluna Tipo Oper
                    st.dataframe(
                        relatorio_dia_anterior,
                        use_container_width=True,
                        hide_index=True
                    )
            
            with tab_canal_venda:
                st.subheader("🛒 Análise por Canal de Venda")
                
                # Análise por canal de venda
                if 'Canal Venda Cliente' in faturado_dia_anterior.columns:
                    # Agrupar por canal de venda
                    relatorio_canal_venda = faturado_dia_anterior.groupby('Canal Venda Cliente').agg({
                        'Quantidade': 'sum',
                        'Vl Net Livro': 'sum',
                        'Item': 'nunique',
                        'Nota Fiscal': 'nunique',
                        'Marca': 'nunique'  # Contar marcas únicas por canal
                    }).reset_index()
                    
                    # Renomear colunas
                    relatorio_canal_venda.columns = ['Canal de Venda', 'Qtd Itens', 'Valor Total', 'SKUs Únicos', 'NFs Únicas', 'Marcas Únicas']
                    
                    # Ordenar por valor total (decrescente)
                    relatorio_canal_venda = relatorio_canal_venda.sort_values('Valor Total', ascending=False)
                    
                    # Formatar valores
                    relatorio_canal_venda['Qtd Itens'] = relatorio_canal_venda['Qtd Itens'].apply(
                        lambda x: formatar_valor_seguro(x, "number")
                    )
                    relatorio_canal_venda['Valor Total'] = relatorio_canal_venda['Valor Total'].apply(
                        lambda x: formatar_valor_seguro(x, "currency")
                    )
                    relatorio_canal_venda['SKUs Únicos'] = relatorio_canal_venda['SKUs Únicos'].apply(
                        lambda x: formatar_valor_seguro(x, "number")
                    )
                    relatorio_canal_venda['NFs Únicas'] = relatorio_canal_venda['NFs Únicas'].apply(
                        lambda x: formatar_valor_seguro(x, "number")
                    )
                    relatorio_canal_venda['Marcas Únicas'] = relatorio_canal_venda['Marcas Únicas'].apply(
                        lambda x: formatar_valor_seguro(x, "number")
                    )
                    
                    # Exibir tabela de canal de venda
                    st.dataframe(
                        relatorio_canal_venda,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Análise detalhada por marca e canal de venda
                    st.subheader("🔍 Detalhamento por Marca e Canal de Venda")
                    
                    # Agrupar por marca e canal de venda
                    relatorio_marca_canal = faturado_dia_anterior.groupby(['Marca', 'Canal Venda Cliente']).agg({
                        'Quantidade': 'sum',
                        'Vl Net Livro': 'sum',
                        'Item': 'nunique',
                        'Nota Fiscal': 'nunique'
                    }).reset_index()
                    
                    # Renomear colunas
                    relatorio_marca_canal.columns = ['Marca', 'Canal de Venda', 'Qtd Itens', 'Valor Total', 'SKUs Únicos', 'NFs Únicas']
                    
                    # Ordenar por marca e depois por valor total
                    relatorio_marca_canal = relatorio_marca_canal.sort_values(['Marca', 'Valor Total'], ascending=[True, False])
                    
                    # Formatar valores
                    relatorio_marca_canal['Qtd Itens'] = relatorio_marca_canal['Qtd Itens'].apply(
                        lambda x: formatar_valor_seguro(x, "number")
                    )
                    relatorio_marca_canal['Valor Total'] = relatorio_marca_canal['Valor Total'].apply(
                        lambda x: formatar_valor_seguro(x, "currency")
                    )
                    relatorio_marca_canal['SKUs Únicos'] = relatorio_marca_canal['SKUs Únicos'].apply(
                        lambda x: formatar_valor_seguro(x, "number")
                    )
                    relatorio_marca_canal['NFs Únicas'] = relatorio_marca_canal['NFs Únicas'].apply(
                        lambda x: formatar_valor_seguro(x, "number")
                    )
                    
                    # Exibir tabela detalhada
                    st.dataframe(
                        relatorio_marca_canal,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Gráfico de barras por canal de venda
                    st.subheader("📊 Gráfico por Canal de Venda")
                    
                    # Preparar dados para o gráfico (valores numéricos)
                    dados_grafico_canal = faturado_dia_anterior.groupby('Canal Venda Cliente').agg({
                        'Vl Net Livro': 'sum',
                        'Quantidade': 'sum'
                    }).reset_index()
                    
                    dados_grafico_canal = dados_grafico_canal.sort_values('Vl Net Livro', ascending=False)
                    
                    # Criar gráfico de barras
                    fig_canal_venda = px.bar(
                        dados_grafico_canal,
                        x='Canal Venda Cliente',
                        y='Vl Net Livro',
                        title=f'💰 Faturamento por Canal de Venda - {dia_anterior.strftime("%d/%m/%Y")}',
                        labels={'Vl Net Livro': 'Valor Total (R$)', 'Canal Venda Cliente': 'Canal de Venda'},
                        color='Vl Net Livro',
                        color_continuous_scale='Blues'
                    )
                    
                    fig_canal_venda.update_layout(
                        xaxis_title="Canal de Venda",
                        yaxis_title="Valor Total (R$)",
                        yaxis_tickprefix="R$ ",
                        plot_bgcolor="#F9F9F9",
                        margin=dict(t=50, b=30),
                        xaxis=dict(tickangle=45)
                    )
                    
                    st.plotly_chart(fig_canal_venda, use_container_width=True)
                    
                else:
                    st.warning("⚠️ Coluna 'Canal Venda Cliente' não encontrada nos dados")
            

            
        else:
            st.warning(f"⚠️ Nenhum item foi faturado em {dia_anterior.strftime('%d/%m/%Y')}")
            
            # Mostrar informações sobre o dia anterior mesmo sem dados
            col_info, col_sugestao = st.columns([1, 1])
            
            with col_info:
                st.info(f"📅 **Data:** {dia_anterior.strftime('%d/%m/%Y')} ({dia_anterior.strftime('%A')})")
            
            with col_sugestao:
                st.info("💡 **Sugestão:** Verifique se há dados disponíveis para esta data ou se foi um dia sem movimento.")
    else:
        st.error("❌ Coluna 'Dt Emis NF' não encontrada nos dados")



# Segundo grupo de abas - Gráficos
tab_fat_diario, tab_fat_marca, tab_potencial = st.tabs(["📆 Faturamento Diário", "📊 Faturamento por Marca", "🎯 Potencial x Faturamento"])

with tab_fat_diario:
# 📈 Gráfico interativo com Plotly Express
    titulo_grafico = formatar_titulo_marcas("📆 Faturamento Diário", marcas_selecionadas, marcas_disponiveis)
        
    fig_fat = px.line(
        faturamento_diario,
        x="Dt Emis NF",
        y="Vl Net Livro",
        markers=True,
        title=titulo_grafico,
        labels={"Dt Emis NF": "Data", "Vl Net Livro": "Faturamento (R$)"},
        hover_data={"Vl Net Livro": False, "vl_formatado": True},
        text="vl_formatado",  # 🎯 Mostrar o valor no ponto
    )

    # ✨ Personalização do layout
    fig_fat.update_traces(
        line=dict(color="blue"),
        marker=dict(size=8),
        textposition="top center",  # Pode usar: 'top center', 'bottom center', 'middle right', etc.
        textfont=dict(size=10),
    )

    fig_fat.update_layout(
        xaxis_title="Data",
        yaxis_title="Faturamento (R$)",
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial"),
        xaxis=dict(tickangle=0),
        yaxis_tickprefix="R$ ",
        margin=dict(t=50, b=30),
    )

    # 📊 Exibir o gráfico
    st.plotly_chart(fig_fat, use_container_width=True, key="faturamento_geral")
    
with tab_fat_marca:
    # 📊 Gráfico de Barras com Plotly
    # 🏷️ Faturamento por Marca - Gráfico Detalhado
    titulo_marca_grafico = formatar_titulo_marcas("📊 Faturamento por Marca - Análise Detalhada", marcas_selecionadas, marcas_disponiveis)
    st.subheader(titulo_marca_grafico)
    
    # Agrupar faturamento por marca e data
    faturamento_marca_data = faturado.groupby(['Marca', 'Dt Emis NF'])['Vl Net Livro'].sum().reset_index()
    
    # Formatar valores para o gráfico
    faturamento_marca_data['vl_formatado'] = faturamento_marca_data['Vl Net Livro'].apply(
        lambda x: formatar_valor_seguro(x, "currency")
    )
    
    # Gráfico de linha por marca
    fig_marca = px.line(
        faturamento_marca_data,
        x="Dt Emis NF",
        y="Vl Net Livro",
        color="Marca",
        markers=True,
        title="📈 Faturamento por Marca ao Longo do Tempo",
        labels={"Dt Emis NF": "Data", "Vl Net Livro": "Faturamento (R$)", "Marca": "Marca"},
        hover_data={"Vl Net Livro": False, "vl_formatado": True},
        color_discrete_map=cores_marca
    )
    
    # Personalização do layout
    fig_marca.update_traces(
        marker=dict(size=6),
        line=dict(width=2)
    )
    
    fig_marca.update_layout(
        xaxis_title="Data",
        yaxis_title="Faturamento (R$)",
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial"),
        xaxis=dict(tickangle=0),
        yaxis_tickprefix="R$ ",
        margin=dict(t=50, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Exibir gráfico
    st.plotly_chart(fig_marca, use_container_width=True, key="faturamento_por_marca")

from datetime import datetime

with tab_potencial:
    # 🎯 Gráfico de Potencial x Faturamento
    titulo_potencial = formatar_titulo_marcas("🎯 Análise de Potencial x Faturamento", marcas_selecionadas, marcas_disponiveis)
    st.subheader(titulo_potencial)
    
    # Mapeamento entre marcas anonimizadas e nomes reais das unidades
    # Este mapeamento deve ser ajustado conforme os dados reais
    mapeamento_marcas_potencial = {
        'MARCA A': 'UNIDADE SOROCABA',
        'MARCA B': 'UNIDADE SAO PAULO', 
        'MARCA C': 'UNIDADE FLORIANOPOLIS',
        'MARCA D': 'UNIDADE CURITIBA'
    }
    
    try:
        # Carregar dados de embarques e calcular potencial
        agrupado_quantidade, agrupado_bu_potencial, embarques_potencial, embarques, hoje_str = etl_embarques.etl_embarques()
        potencial_faturamento = etl_embarques.calcular_potencial_faturamento(embarques, hoje_str)
        
        # Aplicar mapeamento de marcas no DataFrame de potencial
        potencial_faturamento['Unid. Negócio'] = potencial_faturamento['Unid. Negócio'].replace(mapeamento_marcas_potencial)

        # Usar faturamento do período já filtrado pelo usuário (mês/dia selecionado)
        faturado_filtrado_data = faturado.copy()
        if not pd.api.types.is_datetime64_any_dtype(faturado_filtrado_data['Dt Emis NF']):
            faturado_filtrado_data['Dt Emis NF'] = pd.to_datetime(faturado_filtrado_data['Dt Emis NF'], errors='coerce')

        if not potencial_faturamento.empty:
            # Preparar dados para comparação
            # Filtrar unidades excluindo Porto Alegre e Brasília
            marcas_excluidas = ['UNIDADE PORTO ALEGRE', 'UNIDADE BRASILIA']
            
            # Usar faturamento do período filtrado (já aplicado pelos filtros do sidebar)
            faturamento_por_marca_periodo = etl_faturamento.exibir_cards_faturamento_por_marca_bruto(faturado_filtrado_data)
            faturamento_filtrado = faturamento_por_marca_periodo[~faturamento_por_marca_periodo['Marca'].isin(marcas_excluidas)]
            # Criar DataFrame de comparação incluindo todas as marcas com potencial
            # Obter todas as marcas únicas (faturamento + potencial)
            marcas_faturamento = set(faturamento_filtrado['Marca'].tolist())
            marcas_potencial = set(potencial_faturamento['Unid. Negócio'].tolist())
            todas_marcas = marcas_faturamento.union(marcas_potencial)
            
            # Criar DataFrame base
            comparacao_df = pd.DataFrame({
                'Marca': list(todas_marcas),
                'Faturamento_Bruto': 0.0,
                'Potencial': 0.0
            })
            
            # Preencher faturamento
            for idx, row in comparacao_df.iterrows():
                marca = row['Marca']
                faturamento_row = faturamento_filtrado[faturamento_filtrado['Marca'] == marca]
                if not faturamento_row.empty:
                    comparacao_df.at[idx, 'Faturamento_Bruto'] = faturamento_row['Valor'].iloc[0]
            
            # Preencher potencial
            for idx, row in comparacao_df.iterrows():
                marca = row['Marca']
                potencial_row = potencial_faturamento[potencial_faturamento['Unid. Negócio'] == marca]
                if not potencial_row.empty:
                    comparacao_df.at[idx, 'Potencial'] = potencial_row['Potencial_Total'].iloc[0]
            
            # Calcular diferença e percentual
            comparacao_df['Diferenca'] = comparacao_df['Potencial'] - comparacao_df['Faturamento_Bruto']
            comparacao_df['Percentual_Atingido'] = (comparacao_df['Faturamento_Bruto'] / comparacao_df['Potencial'] * 100).round(1)
            comparacao_df['Percentual_Atingido'] = comparacao_df['Percentual_Atingido'].fillna(0)
            
            # Obter cores das marcas
            cores_marca = etl_faturamento.obter_cores_marca()
            
            # Criar gráfico de barras comparativo
            fig_potencial = go.Figure()
            
            # Adicionar barras de faturamento com cores das marcas
            cores_faturamento = [cores_marca.get(marca.upper(), '#1f77b4') for marca in comparacao_df['Marca']]
            
            fig_potencial.add_trace(go.Bar(
                name='Faturamento Bruto',
                x=comparacao_df['Marca'],
                y=comparacao_df['Faturamento_Bruto'],
                marker_color=cores_faturamento,
                text=[formatar_valor_seguro(x, "currency") for x in comparacao_df['Faturamento_Bruto']],
                textposition='outside'
            ))
            
            # Adicionar barras de potencial
            fig_potencial.add_trace(go.Bar(
                name='Potencial Total',
                x=comparacao_df['Marca'],
                y=comparacao_df['Potencial'],
                marker_color='#808080',
                text=[formatar_valor_seguro(x, "currency") for x in comparacao_df['Potencial']],
                textposition='outside'
            ))
            
            # Configurar layout
            fig_potencial.update_layout(
                title='🎯 Comparação: Potencial vs Faturamento Bruto por Marca',
                xaxis_title='Marca',
                yaxis_title='Valor (R$)',
                barmode='group',
                yaxis_tickprefix="R$ ",
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=500,
                
            )
            
            # Layout em colunas: Gráfico à esquerda, Cards à direita
            col_grafico, col_cards = st.columns([2, 1])
            
            with col_grafico:
                st.plotly_chart(fig_potencial, use_container_width=True)
            
            with col_cards:
                
                # Criar cards para cada marca com percentual atingido
                if not comparacao_df.empty:
                    # Filtrar apenas marcas com potencial > 0 para exibir nos cards
                    marcas_com_potencial = comparacao_df[comparacao_df['Potencial'] > 0].copy()
                    
                    if not marcas_com_potencial.empty:
                        # Ordenar por percentual atingido (maior para menor)
                        marcas_com_potencial = marcas_com_potencial.sort_values('Percentual_Atingido', ascending=False)
                        
                        for _, row in marcas_com_potencial.iterrows():
                            marca = row['Marca']
                            percentual = row['Percentual_Atingido']
                            
                            # Definir cor baseada no percentual
                            if percentual >= 100:
                                cor_card = "#28a745"  # Verde - Meta atingida
                                emoji = "🎯"
                            elif percentual >= 80:
                                cor_card = "#ffc107"  # Amarelo - Próximo da meta
                                emoji = "📈"
                            elif percentual >= 50:
                                cor_card = "#fd7e14"  # Laranja - Metade da meta
                                emoji = "⚠️"
                            else:
                                cor_card = "#dc3545"  # Vermelho - Abaixo da meta
                                emoji = "🔴"
                            
                            # Criar card simplificado com HTML/CSS
                            card_html = f"""
                            <div style="
                                background: linear-gradient(135deg, {cor_card}20 0%, {cor_card}40 100%);
                                border: 2px solid {cor_card};
                                border-radius: 12px;
                                padding: 12px;
                                margin: 6px 0;
                                text-align: center;
                                box-shadow: 0 3px 12px rgba(0,0,0,0.1);
                            ">
                                <h4 style="color: {cor_card}; margin: 0 0 8px 0; font-size: 1em;">
                                    {emoji} {marca}
                                </h4>
                                <div style="font-size: 1.8em; font-weight: bold; color: {cor_card}; margin: 0;">
                                    {percentual:.1f}%
                                </div>
                            </div>
                            """
                            
                            st.markdown(card_html, unsafe_allow_html=True)
            
            # DataFrame detalhado como na imagem
            st.subheader("📋 Potencial x Faturado - Receita Sim+Não")
            
            # Preparar dados detalhados
            df_detalhado = pd.DataFrame()
            
            for idx, row in comparacao_df.iterrows():
                marca = row['Marca']
                
                # Buscar dados de embarques para a marca
                embarques_marca = embarques[embarques['Unid. Negócio'] == marca]
                embarques_potencial_marca = embarques_potencial[embarques_potencial['Unid. Negócio'] == marca]
                
                # Calcular métricas de embarques
                qtd_embarques_disponiveis = len(embarques_potencial_marca) if not embarques_potencial_marca.empty else 0
                ticket_medio_embarque = (row['Potencial'] / qtd_embarques_disponiveis) if qtd_embarques_disponiveis > 0 else 0
                
                # Buscar dados de faturamento do período para a marca
                faturado_periodo_marca = faturado_filtrado_data[faturado_filtrado_data['Marca'] == marca]
                faturado_periodo_valor = faturado_periodo_marca['Vl Net Livro'].sum() if not faturado_periodo_marca.empty else 0
                qtd_nfs_periodo = faturado_periodo_marca['Nota Fiscal'].nunique() if not faturado_periodo_marca.empty else 0
                
                # Separar receita sim e não
                if not faturado_periodo_marca.empty:
                    receita_sim = etl_faturamento.filtrar_receita_sim(faturado_periodo_marca)
                    receita_nao = etl_faturamento.filtrar_receita_nao(faturado_periodo_marca)
                    
                    receita_sim_valor = receita_sim['Vl Net Livro'].sum() if not receita_sim.empty else 0
                    receita_nao_valor = receita_nao['Vl Net Livro'].sum() if not receita_nao.empty else 0
                    qtd_nfs_sim = receita_sim['Nota Fiscal'].nunique() if not receita_sim.empty else 0
                    qtd_nfs_nao = receita_nao['Nota Fiscal'].nunique() if not receita_nao.empty else 0
                else:
                    receita_sim_valor = 0
                    receita_nao_valor = 0
                    qtd_nfs_sim = 0
                    qtd_nfs_nao = 0
                
                # Calcular diferença e percentual
                diferenca = row['Potencial'] - faturado_periodo_valor
                percentual = (faturado_periodo_valor / row['Potencial'] * 100) if row['Potencial'] > 0 else 0
                
                # Adicionar linha ao DataFrame
                linha = pd.DataFrame({
                    'UNIDADE DE NEGÓCIO': [marca],
                    'POTENCIAL': [row['Potencial']],
                    'QTD. EMBARQUES DISPONÍVEIS': [qtd_embarques_disponiveis],
                    'TICKET MÉDIO EMBARQUE': [ticket_medio_embarque],
                    'FATURADO PERÍODO': [faturado_periodo_valor],
                    'QTD. NFs': [qtd_nfs_periodo],
                    'RECEITA NÃO': [receita_nao_valor],
                    'QTD. NFs (NÃO)': [qtd_nfs_nao],
                    'DIFERENÇA PREV. X FATURAD': [diferenca],
                    'PERCENTUAL': [percentual]
                })
                
                df_detalhado = pd.concat([df_detalhado, linha], ignore_index=True)
            
            # Adicionar linha de total
            linha_total = pd.DataFrame({
                'UNIDADE DE NEGÓCIO': ['Total Geral'],
                'POTENCIAL': [df_detalhado['POTENCIAL'].sum()],
                'QTD. EMBARQUES DISPONÍVEIS': [df_detalhado['QTD. EMBARQUES DISPONÍVEIS'].sum()],
                'TICKET MÉDIO EMBARQUE': [df_detalhado['POTENCIAL'].sum() / df_detalhado['QTD. EMBARQUES DISPONÍVEIS'].sum() if df_detalhado['QTD. EMBARQUES DISPONÍVEIS'].sum() > 0 else 0],
                'FATURADO PERÍODO': [df_detalhado['FATURADO PERÍODO'].sum()],
                'QTD. NFs': [df_detalhado['QTD. NFs'].sum()],
                'RECEITA NÃO': [df_detalhado['RECEITA NÃO'].sum()],
                'QTD. NFs (NÃO)': [df_detalhado['QTD. NFs (NÃO)'].sum()],
                'DIFERENÇA PREV. X FATURAD': [df_detalhado['DIFERENÇA PREV. X FATURAD'].sum()],
                'PERCENTUAL': [(df_detalhado['FATURADO PERÍODO'].sum() / df_detalhado['POTENCIAL'].sum() * 100) if df_detalhado['POTENCIAL'].sum() > 0 else 0]
            })
            
            df_detalhado = pd.concat([df_detalhado, linha_total], ignore_index=True)
            
            # Formatar valores monetários
            colunas_monetarias = ['POTENCIAL', 'TICKET MÉDIO EMBARQUE', 'FATURADO PERÍODO', 'RECEITA NÃO', 'DIFERENÇA PREV. X FATURAD']
            for col in colunas_monetarias:
                df_detalhado[col] = df_detalhado[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if x != 0 else "R$ -")
            
            # Formatar percentual
            df_detalhado['PERCENTUAL'] = df_detalhado['PERCENTUAL'].apply(lambda x: f"{x:.0f}%" if x > 0 else "0%")
            
            # Formatar quantidades
            colunas_quantidade = ['QTD. EMBARQUES DISPONÍVEIS', 'QTD. NFs', 'QTD. NFs (NÃO)']
            for col in colunas_quantidade:
                df_detalhado[col] = df_detalhado[col].apply(lambda x: f"{x:.0f}" if x > 0 else "0")
            
            # Exibir DataFrame com formatação
            st.dataframe(
                df_detalhado,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "UNIDADE DE NEGÓCIO": st.column_config.TextColumn("UNIDADE DE NEGÓCIO", width="medium"),
                    "POTENCIAL": st.column_config.TextColumn("POTENCIAL", width="medium"),
                    "QTD. EMBARQUES DISPONÍVEIS": st.column_config.TextColumn("QTD. EMBARQUES DISPONÍVEIS", width="medium"),
                    "TICKET MÉDIO EMBARQUE": st.column_config.TextColumn("TICKET MÉDIO EMBARQUE", width="medium"),
                    "FATURADO PERÍODO": st.column_config.TextColumn("FATURADO PERÍODO", width="medium"),
                    "QTD. NFs": st.column_config.TextColumn("QTD. NFs", width="medium"),
                    "RECEITA NÃO": st.column_config.TextColumn("RECEITA NÃO", width="medium"),
                    "QTD. NFs (NÃO)": st.column_config.TextColumn("QTD. NFs (NÃO)", width="medium"),
                    "DIFERENÇA PREV. X FATURAD": st.column_config.TextColumn("DIFERENÇA PREV. X FATURAD", width="medium"),
                    "PERCENTUAL": st.column_config.TextColumn("PERCENTUAL", width="medium")
                }
            )
            
        else:
            st.warning("⚠️ Nenhum dado de potencial encontrado")
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados de potencial: {str(e)}")
        st.info("💡 Verifique se o arquivo de embarques está disponível e acessível")
# Filtros para Marca e Canal Venda Cliente
marcas_disponiveis = faturado['Marca'].dropna().unique()
canais_disponiveis = faturado['Canal Venda Cliente'].dropna().unique()

# ============================================================================
# ANÁLISE DE FATURAMENTO MÊS A MÊS
# ============================================================================

st.subheader("📊 Faturamento Mês a Mês")

# Verificar se há dados e coluna de data (usar dados completos, não filtrados)
if 'Dt Emis NF' in faturado_completo.columns and len(faturado_completo) > 0:
    # Garantir que a coluna de data está no formato correto
    faturado_temporal = faturado_completo.copy()
    if not pd.api.types.is_datetime64_any_dtype(faturado_temporal['Dt Emis NF']):
        faturado_temporal['Dt Emis NF'] = pd.to_datetime(faturado_temporal['Dt Emis NF'], errors='coerce')
    
    # Criar coluna de Mês/Ano
    faturado_temporal['Mes_Ano'] = faturado_temporal['Dt Emis NF'].dt.to_period('M').astype(str)
    
    # Criar abas para análise geral e por unidade
    tab_geral, tab_por_unidade = st.tabs(["📈 Faturamento Geral", "🏢 Faturamento por Unidade"])
    
    with tab_geral:
        st.subheader("Faturamento Total por Mês")
        
        # Agrupar por mês
        faturamento_mensal = faturado_temporal.groupby('Mes_Ano').agg({
            'Vl Net Livro': 'sum',
            'Nota Fiscal': 'nunique',
            'Quantidade': 'sum'
        }).reset_index()
        
        # Renomear colunas
        faturamento_mensal.columns = ['Mês', 'Valor Total', 'NFs Únicas', 'Quantidade Total']
        
        # Ordenar por mês
        faturamento_mensal = faturamento_mensal.sort_values('Mês')
        
        # Criar gráfico de barras
        fig_mensal_geral = px.bar(
            faturamento_mensal,
            x='Mês',
            y='Valor Total',
            title='Faturamento Total por Mês',
            text='Valor Total',
            color_discrete_sequence=['#1E40AF']
        )
        
        # Formatar valores no gráfico
        fig_mensal_geral.update_traces(
            texttemplate='R$ %{text:,.0f}',
            textposition='outside',
            textfont_size=10
        )
        
        fig_mensal_geral.update_layout(
            yaxis_title='Valor Total (R$)',
            xaxis_title='Mês',
            showlegend=False,
            hovermode='x unified'
        )
        
        # Formatar hover
        fig_mensal_geral.update_traces(
            hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
        )
        
        st.plotly_chart(fig_mensal_geral, use_container_width=True, key="faturamento_mensal_geral")
        
        # Mostrar tabela com dados detalhados
        st.subheader("📋 Detalhamento Mensal")
        
        # Formatar valores para exibição
        faturamento_mensal_formatado = faturamento_mensal.copy()
        faturamento_mensal_formatado['Valor Total'] = faturamento_mensal_formatado['Valor Total'].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        faturamento_mensal_formatado['Quantidade Total'] = faturamento_mensal_formatado['Quantidade Total'].apply(
            lambda x: f"{x:,.0f}".replace(",", ".")
        )
        
        st.dataframe(faturamento_mensal_formatado, use_container_width=True, hide_index=True)
        
    with tab_por_unidade:
        st.subheader("Faturamento por Unidade e Mês")
        
        # Agrupar por mês e marca
        faturamento_mensal_marca = faturado_temporal.groupby(['Mes_Ano', 'Marca']).agg({
            'Vl Net Livro': 'sum',
            'Nota Fiscal': 'nunique',
            'Quantidade': 'sum'
        }).reset_index()
        
        # Renomear colunas
        faturamento_mensal_marca.columns = ['Mês', 'Unidade', 'Valor Total', 'NFs Únicas', 'Quantidade Total']
        
        # Ordenar por mês
        faturamento_mensal_marca = faturamento_mensal_marca.sort_values('Mês')
        
        # Obter cores das unidades
        cores_unidades = etl_faturamento.obter_cores_marca()
        
        # Criar gráfico de barras empilhadas
        fig_mensal_marca_empilhado = px.bar(
            faturamento_mensal_marca,
            x='Mês',
            y='Valor Total',
            color='Unidade',
            title='Faturamento Empilhado por Unidade e Mês',
            barmode='stack',
            color_discrete_map=cores_unidades
        )
        
        fig_mensal_marca_empilhado.update_layout(
            yaxis_title='Valor Total (R$)',
            xaxis_title='Mês',
            showlegend=True,
            legend_title_text='Unidade',
            hovermode='x unified'
        )
        
        # Formatar hover
        fig_mensal_marca_empilhado.update_traces(
            hovertemplate='<b>%{fullData.name}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
        )
        
        st.plotly_chart(fig_mensal_marca_empilhado, use_container_width=True, key="faturamento_mensal_marca_empilhado")
        
        # Mostrar tabela pivot
        st.subheader("📋 Tabela Detalhada por Unidade")
        
        # Criar tabela pivot
        tabela_pivot = faturamento_mensal_marca.pivot_table(
            index='Mês',
            columns='Unidade',
            values='Valor Total',
            fill_value=0
        )
        
        # Adicionar coluna de total
        tabela_pivot['Total'] = tabela_pivot.sum(axis=1)
        
        # Formatar valores
        tabela_pivot_formatada = tabela_pivot.applymap(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if x != 0 else "R$ 0,00"
        )
        
        st.dataframe(tabela_pivot_formatada, use_container_width=True)
else:
    st.warning("⚠️ Dados de data não disponíveis para análise mensal")

# ============================================================================
# ANÁLISE POR REGIÃO E ESTADO
# ============================================================================

# 🗺️ Análise por Região e Estado em Abas

tab_estado, tab_regiao = st.tabs(["🗺️ Por Estado", "📍 Por Região"])

with tab_estado:
    titulo_mapa = formatar_titulo_marcas("🗺️ Mapa de Distribuição de Faturamento por Estado", marcas_selecionadas, marcas_disponiveis)
    st.subheader(titulo_mapa)

    # Agrupar por estado - consolidando primeiro por NF para evitar duplicatas
    if 'Estado' in faturado.columns:
        # Consolidar por NF primeiro para evitar duplicatas
        faturado_consolidado_estado = faturado.groupby(['Estado', 'Nota Fiscal']).agg({
            'Vl Net Livro': 'sum',
            'Quantidade': 'sum'
        }).reset_index()
        
        estados_consolidados = faturado_consolidado_estado.groupby('Estado').agg({
            'Nota Fiscal': 'nunique',  # Conta notas fiscais únicas por estado
            'Vl Net Livro': 'sum',     # Soma valor total por estado
            'Quantidade': 'sum'        # Soma quantidade total por estado
        }).reset_index()

        estados_consolidados = estados_consolidados.rename(columns={
            'Nota Fiscal': 'Qtd NFs',
            'Vl Net Livro': 'Valor Total',
            'Quantidade': 'Qtd Total'
        })

        # Ordenar do maior para o menor valor total
        estados_consolidados = estados_consolidados.sort_values('Valor Total', ascending=False)
        
        # Debug: Mostrar total para verificação
        total_faturamento_estados = estados_consolidados['Valor Total'].sum()
        st.info(f"🔍 **Total de Faturamento por Estado:** {formatar_valor_seguro(total_faturamento_estados, 'currency')}")

        def carregar_dados_geojson():
            """
            Carrega os dados do arquivo br_states.json (GeoJSON dos estados brasileiros)
            """
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # O arquivo br_states.json está na raiz do projeto
                geojson_path = os.path.join(current_dir, 'br_states.json')
                
                with open(geojson_path, 'r', encoding='utf-8') as f:
                    geojson_data = json.load(f)
                
                return geojson_data
            except Exception as e:
                st.error(f"Erro ao carregar dados do GeoJSON: {e}")
                return None

        def criar_mapa_coropletico(estados_consolidados):
            """
            Cria um mapa coroplético dos estados brasileiros baseado no valor de faturamento
            """
            # Carregar dados do GeoJSON
            geojson_data = carregar_dados_geojson()
            
            if geojson_data is None:
                return None
            
            # Criar dicionário com dados dos estados para o mapa
            estados_map = {}
            for _, estado in estados_consolidados.iterrows():
                estados_map[estado['Estado']] = {
                    'Qtd NFs': estado['Qtd NFs'],
                    'Valor Total': estado['Valor Total'],
                    'Qtd Total': estado['Qtd Total']
                }
            
            # Criar o mapa coroplético baseado no valor total de faturamento por estado
            fig = go.Figure(go.Choroplethmapbox(
                geojson=geojson_data,
                locations=list(estados_map.keys()),
                z=[estados_map[estado]['Valor Total'] for estado in estados_map.keys()],
                colorscale='Blues',
                colorbar_title="Faturamento Total (R$)",
                hovertemplate="<b>%{location}</b><br>" +
                             "Valor Total: R$ %{z:,.2f}<br>" +
                             "Qtd NFs: %{customdata[0]:,.0f}<br>" +
                             "Qtd Total: %{customdata[1]:,.0f}<br>" +
                             "<extra></extra>",
                customdata=[[estados_map[estado]['Qtd NFs'], estados_map[estado]['Qtd Total']] for estado in estados_map.keys()],
                marker_opacity=0.8,
                marker_line_width=1,
                marker_line_color='white'
            ))
            
            # Configurar layout do mapa com fundo branco
            fig.update_layout(
                mapbox_style="white-bg",
                mapbox_zoom=3.2,
                mapbox_center={"lat": -14.2350, "lon": -51.9253},
                margin={"r": 50, "t": 50, "l": 50, "b": 50},
                height=600,
                title={
                    'text': "Distribuição de Faturamento por Estado",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20}
                }
            )
            
            return fig

        # Criar o mapa coroplético
        mapa_coropletico = criar_mapa_coropletico(estados_consolidados)
        
        if mapa_coropletico:
            # Layout em duas colunas
            col_mapa, col_tabela = st.columns([2, 1])
            
            with col_mapa:
                st.plotly_chart(mapa_coropletico, use_container_width=True)
            
            with col_tabela:
                # Mostrar tabela de resumo por estado
                st.subheader("📋 Resumo por Estado")
                
                # Formatar valores para exibição
                estados_consolidados['Valor Total Formatado'] = estados_consolidados['Valor Total'].apply(
                    lambda x: formatar_valor_seguro(x, "currency")
                )
                estados_consolidados['Qtd NFs Formatado'] = estados_consolidados['Qtd NFs'].apply(
                    lambda x: formatar_valor_seguro(x, "number")
                )
                estados_consolidados['Qtd Total Formatado'] = estados_consolidados['Qtd Total'].apply(
                    lambda x: formatar_valor_seguro(x, "number")
                )
                
                # Calcular percentual do total
                total_faturamento_estados = estados_consolidados['Valor Total'].sum()
                estados_consolidados['Percentual'] = (estados_consolidados['Valor Total'] / total_faturamento_estados * 100).round(2)
                
                # Preparar dados para exibição
                df_exibicao_estados = estados_consolidados[['Estado', 'Valor Total Formatado', 'Qtd NFs Formatado', 'Qtd Total Formatado', 'Percentual']].copy()
                df_exibicao_estados.columns = ['Estado', 'Valor Total', 'Qtd NFs', 'Qtd Total', '% do Total']
                
                st.dataframe(df_exibicao_estados, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Não foi possível carregar o mapa. Verifique se o arquivo br_states.json está disponível.")
    else:
        st.warning("⚠️ Coluna 'Estado' não encontrada nos dados para criar o mapa.")



with tab_regiao:
    titulo_regiao = formatar_titulo_marcas("🗺️ Análise de Faturamento por Região", marcas_selecionadas, marcas_disponiveis)
    st.subheader(titulo_regiao)

    # Calcular faturamento por região - consolidando primeiro por NF para evitar duplicatas
    faturado_consolidado_regiao = faturado.groupby(['Região', 'Nota Fiscal'])['Vl Net Livro'].sum().reset_index()
    faturamento_por_regiao = faturado_consolidado_regiao.groupby('Região')['Vl Net Livro'].sum().sort_values(ascending=False)

    # Calcular quantidade de registros por região
    registros_por_regiao = faturado.groupby('Região').size().sort_values(ascending=False)

    # Criar DataFrame para análise
    df_regiao = pd.DataFrame({
        'Região': faturamento_por_regiao.index,
        'Faturamento': faturamento_por_regiao.values,
        'Registros': registros_por_regiao.values
    })

    # Calcular percentual do total
    total_faturamento = df_regiao['Faturamento'].sum()
    df_regiao['Percentual'] = (df_regiao['Faturamento'] / total_faturamento * 100).round(2)

    # Debug: Mostrar total para verificação
    st.info(f"🔍 **Total de Faturamento por Região:** {formatar_valor_seguro(total_faturamento, 'currency')}")

    # Formatar valores
    df_regiao['Faturamento_Formatado'] = df_regiao['Faturamento'].apply(
        lambda x: formatar_valor_seguro(x, "currency")
    )
    df_regiao['Registros_Formatado'] = df_regiao['Registros'].apply(
        lambda x: formatar_valor_seguro(x, "number")
    )

    # Layout em duas colunas
    col_grafico, col_tabela = st.columns(2)

    with col_grafico:
        # Gráfico de barras por região
        fig_regiao = px.bar(
            df_regiao,
            x='Região',
            y='Faturamento',
            title='📊 Faturamento por Região',
            labels={'Faturamento': 'Faturamento (R$)', 'Região': 'Região'},
            color='Região',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_regiao.update_layout(
            yaxis_tickprefix="R$ ",
            xaxis_title="Região",
            yaxis_title="Faturamento (R$)",
            showlegend=False,
            plot_bgcolor="#FFFFFF",
            margin=dict(t=50, b=30),
        )
        
        st.plotly_chart(fig_regiao, use_container_width=True)

    with col_tabela:
        # Tabela de resumo por região
        st.subheader("📋 Resumo por Região")
        
        # Preparar dados para exibição
        df_exibicao = df_regiao[['Região', 'Faturamento_Formatado', 'Registros_Formatado', 'Percentual']].copy()
        df_exibicao.columns = ['Região', 'Faturamento', 'Qtd Registros', '% do Total']
        
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)







# Exibir dataframe filtrado

# Adiciona a coluna 'Lead Time' ao DataFrame filtrado
# Definir faturado_filtrado para uso nos gráficos de lead time
faturado_filtrado = faturado.copy()
# Para cálculo de lead time, sempre usar apenas Receita Sim
faturado_filtrado = etl_faturamento.filtrar_receita_sim(faturado_filtrado)

# Debug: verificar se há dados
if len(faturado_filtrado) == 0:
    st.warning(f"⚠️ Nenhum dado encontrado após filtros para cálculo de lead time (Receita Sim). Verifique os filtros de mês/marca selecionados.")
    faturado_filtrado_lead = pd.DataFrame()
else:
    faturado_filtrado_lead = etl_faturamento.adicionar_lead_time(faturado_filtrado)

# DataFrame removido - apenas gráficos de lead time e NFs acumuladas serão exibidos

# Seção de Lead Time com Abas
st.subheader("⏱️ Análise de Lead Time")

# Preparar dados de lead time antes das tabs
if len(faturado_filtrado_lead) == 0:
    faturado_filtrado_lead_unidades_principais = pd.DataFrame()
    faturado_filtrado_lead_unidades_principais_unicas = pd.DataFrame()
    tem_dados_lead_time = False
else:
    # Filtrar apenas unidades principais (Sorocaba, São Paulo, Florianópolis) para cálculo de lead time
    faturado_filtrado_lead_unidades_principais = faturado_filtrado_lead[faturado_filtrado_lead['Marca'].str.upper().isin(['UNIDADE SOROCABA', 'UNIDADE SAO PAULO', 'UNIDADE FLORIANOPOLIS'])]
    
    # Usar apenas notas fiscais únicas para cálculo de lead time
    faturado_filtrado_lead_unidades_principais_unicas = faturado_filtrado_lead_unidades_principais.drop_duplicates(subset=['Nota Fiscal'])
    tem_dados_lead_time = len(faturado_filtrado_lead_unidades_principais_unicas) > 0

# Criar abas para organizar os gráficos de lead time
tab_lead_time_1, tab_lead_time_2, tab_lead_time_3, tab_lead_time_4 = st.tabs([
    "📊 Lead Time Médio por Marca",
    "📈 Quantidade por D+ e Marca", 
    "📊 Percentual por Marca em cada D+",
    "📅 Lead Time Diário"
])

with tab_lead_time_1:
    # Gráfico de barras: Lead Time médio por unidade
    
    # Verificar se há dados para processar
    if not tem_dados_lead_time:
        st.info("⏱️ Lead Time Médio não disponível para o filtro atual. Nenhum dado de faturamento (Receita Sim) encontrado para as unidades principais.")
    else:
        
        # Calcular lead time médio por unidade (usando apenas NFs únicas)
        lead_time_por_marca = (
            faturado_filtrado_lead_unidades_principais_unicas
            .groupby('Marca', as_index=False)['Lead Time']
            .mean()
            .rename(columns={'Lead Time': 'Lead Time Médio'})
        )
        
        if not lead_time_por_marca.empty:
            # Obter cores padronizadas das unidades
            cores_marca = etl_faturamento.obter_cores_marca()
            
            fig = px.bar(
                lead_time_por_marca,
                x='Marca',
                y='Lead Time Médio',
                title='Lead Time Médio por Unidade (Sorocaba, São Paulo, Florianópolis)',
                color='Marca',
                color_discrete_map=cores_marca
            )
            
            fig.update_layout(
                yaxis_title='Lead Time Médio (dias)',
                xaxis_title='Marca',
                showlegend=False
            )
            
            fig.update_traces(
                texttemplate='%{y:.2f}',
                textposition='outside'
            )
            
            st.plotly_chart(fig, use_container_width=True, key="lead_time_medio_marca")
        else:
            st.info("⏱️ Lead Time Médio não disponível para o filtro atual. Após filtrar pelas unidades principais, nenhum dado foi encontrado.")


with tab_lead_time_2:
    # Gráfico de Quantidade de NFs por D+ e Marca
    st.subheader("📊 Quantidade de Notas Fiscais por D+ e Marca")
    
    if not tem_dados_lead_time:
        st.info("⏱️ Nenhum dado disponível para o filtro atual.")
    else:
        # Calcular distribuição por D+ e Unidade (usando apenas NFs únicas)
        distribuicao_d_mais_marca = (
            faturado_filtrado_lead_unidades_principais_unicas
        .groupby(['D+', 'Marca'], as_index=False)
        .size()
        .rename(columns={'size': 'Quantidade'})
        )

        # Ordenar por D+ para melhor visualização
        ordem_d_mais = ['D+0', 'D+1', 'D+2', 'D+3', 'D+4', 'D+5', 'N/A']
        distribuicao_d_mais_marca['D+'] = pd.Categorical(distribuicao_d_mais_marca['D+'], categories=ordem_d_mais, ordered=True)
        distribuicao_d_mais_marca = distribuicao_d_mais_marca.sort_values(['D+', 'Marca'])

        if not distribuicao_d_mais_marca.empty:
            # Obter cores padronizadas das unidades
            cores_marca = etl_faturamento.obter_cores_marca()
            
            # Criar gráfico de barras agrupadas
            fig_d_mais_marca = px.bar(
                distribuicao_d_mais_marca,
                x='D+',
                y='Quantidade',
                color='Marca',
                title='Quantidade de Notas Fiscais por D+ e Unidade (Principais)',
                barmode='stack',
                color_discrete_map=cores_marca
            )
            
            fig_d_mais_marca.update_layout(
                yaxis_title='Quantidade de Notas Fiscais',
                xaxis_title='Classificação D+',
                showlegend=True
            )
            
            fig_d_mais_marca.update_traces(
                texttemplate='%{y}',
                textposition='outside'
            )
            
            st.plotly_chart(fig_d_mais_marca, use_container_width=True, key="quantidade_d_mais_marca")
            
            # Mostrar tabela com os dados
            st.subheader("📋 Distribuição Detalhada por D+ e Marca")
            
            # Criar tabela pivot para melhor visualização
            tabela_d_mais_marca = distribuicao_d_mais_marca.pivot_table(
                index='D+',
                columns='Marca',
                values='Quantidade',
                fill_value=0
            )
            
            # Calcular totais por linha e coluna
            tabela_d_mais_marca['Total'] = tabela_d_mais_marca.sum(axis=1)
            tabela_d_mais_marca.loc['Total'] = tabela_d_mais_marca.sum(axis=0)
            
            st.dataframe(tabela_d_mais_marca, use_container_width=True)
            
        else:
            st.info("📅 Nenhum dado disponível para distribuição por D+ e Marca.")

with tab_lead_time_3:
    # Gráfico de Percentual por Marca em cada D+
    st.subheader("📊 Percentual por Marca em cada D+")
    
    if not tem_dados_lead_time:
        st.info("⏱️ Nenhum dado disponível para o filtro atual.")
    else:
        # Calcular distribuição por D+ e Unidade (usando apenas NFs únicas)
        distribuicao_d_mais_marca = (
            faturado_filtrado_lead_unidades_principais_unicas
            .groupby(['D+', 'Marca'], as_index=False)
            .size()
            .rename(columns={'size': 'Quantidade'})
        )
        
        # Usar os mesmos dados da aba anterior
        if not distribuicao_d_mais_marca.empty:
            # Obter cores padronizadas das unidades
            cores_marca = etl_faturamento.obter_cores_marca()
            
            # Calcular percentuais
            percentual_d_mais_marca = distribuicao_d_mais_marca.copy()
            total_por_marca = distribuicao_d_mais_marca.groupby('Marca')['Quantidade'].sum()
            
            percentual_d_mais_marca['Percentual'] = percentual_d_mais_marca.apply(
                lambda row: (row['Quantidade'] / total_por_marca[row['Marca']] * 100).round(2), 
                axis=1
            )
            
            # Criar tabela pivot com percentuais
            tabela_percentual = percentual_d_mais_marca.pivot_table(
                index='D+',
                columns='Marca',
                values='Percentual',
                fill_value=0
            )
            
            # Criar layout em colunas: gráfico de torta + tabela
            col_torta, col_tabela = st.columns([1, 1])
            
            with col_torta:
                # Criar gráfico de torta para percentual por marca em cada D+
                fig_torta = px.pie(
                    percentual_d_mais_marca,
                    values='Percentual',
                    names='Marca',
                    title='Distribuição Percentual por Marca',
                    color='Marca',
                    color_discrete_map=cores_marca
                )
                
                fig_torta.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Percentual: %{percent}<br>Quantidade: %{customdata}',
                    customdata=percentual_d_mais_marca['Quantidade']
                )
                
                fig_torta.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.01
                    )
                )
                
                st.plotly_chart(fig_torta, use_container_width=True, key="percentual_torta_marca")
            
            with col_tabela:
                st.dataframe(tabela_percentual, use_container_width=True)
            
        else:
            st.info("📅 Nenhum dado disponível para percentual por D+ e Marca.")

with tab_lead_time_4:
    # Gráfico de Lead Time Diário
    st.subheader("📊 Lead Time Diário")
    
    if not tem_dados_lead_time:
        st.info("⏱️ Nenhum dado disponível para o filtro atual.")
    else:
        # Filtrar apenas outubro de 2025 e excluir finais de semana (usando apenas NFs únicas)
        faturado_outubro = faturado_filtrado_lead_unidades_principais_unicas[
            (faturado_filtrado_lead_unidades_principais_unicas['Dt Emis NF'].dt.year == 2025) &
            (faturado_filtrado_lead_unidades_principais_unicas['Dt Emis NF'].dt.month == 10)
        ].copy()
        
        # Adicionar coluna de dia da semana (0=segunda, 6=domingo)
        faturado_outubro['dia_semana'] = faturado_outubro['Dt Emis NF'].dt.dayofweek
        
        # Filtrar apenas dias úteis (segunda a sexta: 0,1,2,3,4)
        faturado_outubro_dias_uteis = faturado_outubro[faturado_outubro['dia_semana'] <= 4].copy()
        
        # Calcular lead time médio por dia
        lead_time_diario_outubro = (
            faturado_outubro_dias_uteis
            .groupby(['Dt Emis NF', 'Marca'], as_index=False)['Lead Time']
            .mean()
            .rename(columns={'Lead Time': 'Lead Time Médio Diário'})
        )
        
        # Adicionar coluna de dia do mês
        lead_time_diario_outubro['Dia'] = lead_time_diario_outubro['Dt Emis NF'].dt.day
        
        if not lead_time_diario_outubro.empty:
            # Obter cores padronizadas das unidades
            cores_marca = etl_faturamento.obter_cores_marca()
            
            # Criar gráfico de coluna para lead time diário
            fig_diario = px.bar(
                lead_time_diario_outubro,
                x='Dia',
                y='Lead Time Médio Diário',
                color='Marca',
                title='Lead Time Médio Diário por Unidade - Outubro 2025 (Dias Úteis)',
                barmode='group',
                color_discrete_map=cores_marca
            )
            
            # Configurar layout
            fig_diario.update_layout(
                yaxis_title='Lead Time Médio (dias)',
                xaxis_title='Dia do Mês',
                showlegend=True
            )
            
            # Adicionar valores nas barras
            fig_diario.update_traces(
                texttemplate='%{y:.2f}',
                textposition='outside'
            )
            
            st.plotly_chart(fig_diario, use_container_width=True, key="lead_time_diario_outubro")
            
            # Mostrar tabela com os dados
            st.subheader("📋 Dados Detalhados - Lead Time Diário")
            tabela_diaria = lead_time_diario_outubro.pivot_table(
                index='Dia',
                columns='Marca',
                values='Lead Time Médio Diário',
                aggfunc='mean'
            ).round(2)
            
            st.dataframe(tabela_diaria, use_container_width=True)

# ============================================================================
# SEÇÃO DE DEVOLUÇÃO
# ============================================================================

st.subheader("📦 Análise de Devoluções")

# Carregar dados de devolução com cache
@st.cache_data(ttl=300)
def carregar_dados_devolucao_com_cache():
    """Carrega dados de devolução com cache."""
    return etl_faturamento.carregar_dados_devolucao()

# Carregar dados de devolução
df_devolucao = carregar_dados_devolucao_com_cache()

# Aplicar filtros de data se existirem
if 'faturado_filtrado' in locals() and len(faturado_filtrado) > 0:
    # Usar as mesmas datas do faturamento filtrado
    data_inicio = faturado_filtrado['Dt Emis NF'].min()
    data_fim = faturado_filtrado['Dt Emis NF'].max()
    
    # Filtrar devoluções pelo mesmo período
    df_devolucao = df_devolucao[
        (df_devolucao['Dt Emis NF'] >= data_inicio) & 
        (df_devolucao['Dt Emis NF'] <= data_fim)
    ]

# Calcular métricas de devolução
metricas_devolucao = etl_faturamento.calcular_metricas_devolucao(df_devolucao)

# Exibir métricas principais
if len(df_devolucao) > 0:
    col_dev1, col_dev2, col_dev3 = st.columns(3)
    
    with col_dev1:
        st.metric(
            "💰 Total Devoluções", 
            f"R$ {metricas_devolucao['total_devolucao']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
    
    with col_dev2:
        st.metric(
            "📦 Quantidade Devolvida", 
            f"{metricas_devolucao['qtd_devolucao']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
    
    with col_dev3:
        st.metric(
            "📊 Valor Médio", 
            f"R$ {metricas_devolucao['media_devolucao']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
else:
    st.warning("⚠️ Nenhuma devolução encontrada no período selecionado")

# Cards de devolução por marca
if len(df_devolucao) > 0 and len(metricas_devolucao['devolucao_por_marca']) > 0:
    st.subheader("🏷️ Valor Devolvido por Marca")
    
    # Obter cores para devolução
    cores_devolucao = etl_faturamento.obter_cores_devolucao()
    
    # Calcular total geral
    total_geral = metricas_devolucao['devolucao_por_marca'].sum()
    
    # Criar cards para cada marca
    col_dev_cards = st.columns(4)
    
    for i, (marca, valor) in enumerate(metricas_devolucao['devolucao_por_marca'].items()):
        # Calcular percentual
        percentual = (valor / total_geral) * 100
        
        # Determinar cor baseada na marca
        cor_marca = cores_devolucao.get(marca, "#dc3545")
        
        # Formatar valor
        valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Escolher coluna baseada no índice
        col_idx = i % 4
        with col_dev_cards[col_idx]:
            st.markdown(f"""
            <div class="card-devolucao" style="background: linear-gradient(135deg, {cor_marca} 0%, {cor_marca}CC 100%); border-left: 4px solid {cor_marca};">
                <div class="card-title-devolucao">{marca}</div>
                <div class="card-value-devolucao">{valor_formatado}</div>
                <div class="card-subtitle-devolucao">{percentual:.1f}% do total</div>
            </div>
            """, unsafe_allow_html=True)

# Criar abas para diferentes visualizações de devolução
if len(df_devolucao) > 0:
    tab_dev1, tab_dev2, tab_dev3, tab_dev4 = st.tabs(["📊 Devoluções por Marca", "📈 Evolução das Devoluções", "📋 Dados Detalhados", "🔝 Top Itens com Maior Índice de Devolução"])
    
    with tab_dev1:
        # Gráfico de torta - Devoluções por marca
        if len(metricas_devolucao['devolucao_por_marca']) > 0:
            fig_torta_devolucao = px.pie(
                metricas_devolucao['devolucao_por_marca'].reset_index(),
                values='Vl Net Livro',
                names='Marca',
                title="📦 Devoluções por Marca",
                color_discrete_map=cores_devolucao
            )
            
            # Personalização do gráfico de torta
            fig_torta_devolucao.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hole=0.3  # Torta com buraco no meio
            )
            
            fig_torta_devolucao.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.02
                )
            )
            
            # Preparar dados da tabela
            resumo_devolucao = metricas_devolucao['devolucao_por_marca'].reset_index()
            resumo_devolucao['Percentual'] = (resumo_devolucao['Vl Net Livro'] / resumo_devolucao['Vl Net Livro'].sum() * 100).round(1)
            resumo_devolucao['Valor Formatado'] = resumo_devolucao['Vl Net Livro'].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            
            resumo_devolucao = resumo_devolucao[['Marca', 'Vl Net Livro', 'Percentual']]
            resumo_devolucao.columns = ['Marca', 'Valor (R$)', '% do Total']
            
            # Layout em colunas lado a lado
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.plotly_chart(fig_torta_devolucao, use_container_width=True, key="torta_devolucao")
            
            with col2:
                st.subheader("📋 Resumo de Devoluções por Marca")
                st.dataframe(
                    resumo_devolucao,
                    column_config={
                        "Valor (R$)": st.column_config.TextColumn("Valor (R$)", width="medium"),
                        "% do Total": st.column_config.NumberColumn("% do Total", format="%.1f%%")
                    },
                    hide_index=True,
                    use_container_width=True
                )
    
    with tab_dev2:
        # Evolução das Devoluções ao Longo do Tempo
        if 'Dt Emis NF' in df_devolucao.columns:
            devolucao_diaria = df_devolucao.groupby("Dt Emis NF", as_index=False)["Vl Net Livro"].sum()
            
            if len(devolucao_diaria) > 0:
                # Formatar valores para tooltip
                devolucao_diaria["vl_formatado"] = devolucao_diaria["Vl Net Livro"].apply(
                    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                
                # Gráfico de linha - Evolução das devoluções
                fig_devolucao_linha = px.line(
                    devolucao_diaria,
                    x="Dt Emis NF",
                    y="Vl Net Livro",
                    markers=True,
                    title="📈 Evolução das Devoluções Diárias",
                    labels={"Dt Emis NF": "Data", "Vl Net Livro": "Valor Devolvido (R$)"},
                    hover_data={"Vl Net Livro": False, "vl_formatado": True},
                    text="vl_formatado",
                )
                
                # Personalização do layout
                fig_devolucao_linha.update_traces(
                    line=dict(color="red"),
                    marker=dict(size=8),
                    textposition="top center",
                    textfont=dict(size=10),
                )
                
                fig_devolucao_linha.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Valor Devolvido (R$)",
                    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial"),
                    xaxis=dict(tickangle=0),
                    yaxis_tickprefix="R$ ",
                    plot_bgcolor="#F9F9F9",
                    margin=dict(t=50, b=30),
                )
                
                st.plotly_chart(fig_devolucao_linha, use_container_width=True, key="devolucao_linha")
                
                # Gráfico de linha por marca
                st.subheader("📈 Devoluções por Marca ao Longo do Tempo")
                devolucao_marca_data = df_devolucao.groupby(['Marca', 'Dt Emis NF'])['Vl Net Livro'].sum().reset_index()
                
                # Formatar valores para o gráfico
                devolucao_marca_data['vl_formatado'] = devolucao_marca_data['Vl Net Livro'].apply(
                    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                
                # Gráfico de linha por marca
                fig_devolucao_marca = px.line(
                    devolucao_marca_data,
                    x="Dt Emis NF",
                    y="Vl Net Livro",
                    color="Marca",
                    markers=True,
                    title="📈 Devoluções por Marca ao Longo do Tempo",
                    labels={"Dt Emis NF": "Data", "Vl Net Livro": "Valor Devolvido (R$)", "Marca": "Marca"},
                    hover_data={"Vl Net Livro": False, "vl_formatado": True},
                    color_discrete_map=cores_devolucao
                )
                
                # Personalização do layout
                fig_devolucao_marca.update_traces(
                    marker=dict(size=6),
                    line=dict(width=2)
                )
                
                fig_devolucao_marca.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Valor Devolvido (R$)",
                    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial"),
                    xaxis=dict(tickangle=0),
                    yaxis_tickprefix="R$ ",
                    plot_bgcolor="#F9F9F9",
                    margin=dict(t=50, b=30),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig_devolucao_marca, use_container_width=True, key="devolucao_por_marca")
            else:
                st.info("📈 Nenhuma devolução encontrada para o período selecionado")
        else:
            st.warning("⚠️ Coluna de data não encontrada para análise temporal")
    
    with tab_dev3:
        # Exibir DataFrame de Devoluções
        st.subheader("📋 Dados Detalhados de Devoluções")
        
        # Formatar a coluna de data para exibição
        if 'Dt Emis NF' in df_devolucao.columns:
            df_devolucao_display = df_devolucao.copy()
            df_devolucao_display['Dt Emis NF'] = df_devolucao_display['Dt Emis NF'].dt.strftime('%d/%m/%Y')
        else:
            df_devolucao_display = df_devolucao.copy()
        
        st.dataframe(df_devolucao_display, use_container_width=True)
    
    with tab_dev4:
        # Top itens com maior índice de devolução por marca
        st.subheader("🔝 Top Itens com Maior Índice de Devolução por Marca")
        
        # Calcular índice de devolução por item (se temos dados de faturamento para comparação)
        if 'faturado' in locals() and len(faturado) > 0:
            # Verificar se as colunas necessárias existem
            colunas_faturado = ['Item', 'Desc Item', 'Vl Net Livro', 'Quantidade', 'Marca']
            colunas_devolucao = ['Item', 'Desc Item', 'Vl Net Livro', 'Quantidade', 'Marca']
            
            if all(col in faturado.columns for col in colunas_faturado) and all(col in df_devolucao.columns for col in colunas_devolucao):
                # Obter marcas disponíveis que têm devoluções
                marcas_com_devolucao = df_devolucao['Marca'].unique()
                marcas_com_faturamento = faturado['Marca'].unique()
                marcas_validas = list(set(marcas_com_devolucao) & set(marcas_com_faturamento))
                
                if len(marcas_validas) > 0:
                    # Criar subabas para cada marca
                    tabs_marcas = st.tabs([f"🏷️ {marca}" for marca in sorted(marcas_validas)])
                    
                    for i, marca in enumerate(sorted(marcas_validas)):
                        with tabs_marcas[i]:
                            st.subheader(f"📊 Análise de Devolução - {marca}")
                            
                            # Filtrar dados por marca
                            faturado_marca = faturado[faturado['Marca'] == marca]
                            devolucao_marca = df_devolucao[df_devolucao['Marca'] == marca]
                            
                            if len(faturado_marca) > 0 and len(devolucao_marca) > 0:
                                # Agrupar devoluções por item para a marca
                                devolucao_por_item = devolucao_marca.groupby(['Item', 'Desc Item'], as_index=False).agg({
                                    'Vl Net Livro': 'sum',
                                    'Quantidade': 'sum'
                                }).rename(columns={'Quantidade': 'Qtde_Devolvida'})
                                
                                # Agrupar faturamento por item para a marca
                                faturamento_por_item = faturado_marca.groupby(['Item', 'Desc Item'], as_index=False).agg({
                                    'Vl Net Livro': 'sum',
                                    'Quantidade': 'sum'
                                }).rename(columns={'Quantidade': 'Qtde_Faturada'})
                                
                                # Fazer merge dos dados
                                analise_devolucao = pd.merge(
                                    devolucao_por_item, 
                                    faturamento_por_item, 
                                    on=['Item', 'Desc Item'], 
                                    how='inner'
                                )
                                
                                if len(analise_devolucao) > 0:
                                    # Calcular índice de devolução
                                    analise_devolucao['Indice_Devolucao_Valor'] = (
                                        analise_devolucao['Vl Net Livro_x'] / analise_devolucao['Vl Net Livro_y'] * 100
                                    ).round(2)
                                    
                                    analise_devolucao['Indice_Devolucao_Qtd'] = (
                                        analise_devolucao['Qtde_Devolvida'] / analise_devolucao['Qtde_Faturada'] * 100
                                    ).round(2)
                                    
                                    # Filtrar apenas itens com devolução significativa
                                    analise_devolucao = analise_devolucao[analise_devolucao['Vl Net Livro_x'] > 0]
                                    
                                    # Ordenar por índice de devolução (valor)
                                    top_devolucao = analise_devolucao.sort_values('Indice_Devolucao_Valor', ascending=False).head(15)
                                    
                                    if len(top_devolucao) > 0:
                                        # Layout em colunas para gráfico e tabela
                                        col1, col2 = st.columns([1, 1])
                                        
                                        with col1:
                                            # Gráfico de barras dos top 10
                                            if len(top_devolucao) >= 1:
                                                top_grafico = top_devolucao.head(10)
                                                
                                                fig_top_devolucao = px.bar(
                                                    top_grafico,
                                                    x='Indice_Devolucao_Valor',
                                                    y='Desc Item',
                                                    orientation='h',
                                                    title=f"🔝 Top {len(top_grafico)} Itens - {marca}",
                                                    labels={'Indice_Devolucao_Valor': 'Índice de Devolução (%)', 'Desc Item': 'Item'},
                                                    color='Indice_Devolucao_Valor',
                                                    color_continuous_scale='Reds'
                                                )
                                                
                                                fig_top_devolucao.update_layout(
                                                    height=400,
                                                    yaxis={'categoryorder': 'total ascending'}
                                                )
                                                
                                                st.plotly_chart(fig_top_devolucao, use_container_width=True)
                                            else:
                                                st.info(f"📊 Não há dados suficientes para gerar gráfico para {marca}")
                                        
                                        with col2:
                                            # Preparar dados para exibição
                                            top_devolucao_display = top_devolucao.copy()
                                            top_devolucao_display['Valor_Devolvido'] = top_devolucao_display['Vl Net Livro_x'].apply(
                                                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                                            )
                                            top_devolucao_display['Valor_Faturado'] = top_devolucao_display['Vl Net Livro_y'].apply(
                                                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                                            )
                                            
                                            # Selecionar colunas para exibição
                                            colunas_exibir = [
                                                'Item', 'Desc Item', 'Valor_Devolvido', 'Valor_Faturado', 
                                                'Indice_Devolucao_Valor', 'Qtde_Devolvida', 'Qtde_Faturada', 'Indice_Devolucao_Qtd'
                                            ]
                                            
                                            top_devolucao_display = top_devolucao_display[colunas_exibir]
                                            top_devolucao_display.columns = [
                                                'Código', 'Descrição', 'Valor Devolvido', 'Valor Faturado', 
                                                'Índice Dev. (%)', 'Qtd Devolvida', 'Qtd Faturada', 'Índice Dev. Qtd (%)'
                                            ]
                                            
                                            # Exibir tabela
                                            st.dataframe(
                                                top_devolucao_display,
                                                column_config={
                                                    "Índice Dev. (%)": st.column_config.NumberColumn("Índice Dev. (%)", format="%.2f%%"),
                                                    "Índice Dev. Qtd (%)": st.column_config.NumberColumn("Índice Dev. Qtd (%)", format="%.2f%%"),
                                                    "Qtd Devolvida": st.column_config.NumberColumn("Qtd Devolvida", format="%d"),
                                                    "Qtd Faturada": st.column_config.NumberColumn("Qtd Faturada", format="%d")
                                                },
                                                hide_index=True,
                                                use_container_width=True
                                            )
                                        
                                        # Métricas resumidas da marca
                                        st.subheader(f"📈 Resumo - {marca}")
                                        
                                        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
                                        
                                        with col_met1:
                                            total_devolvido = top_devolucao['Vl Net Livro_x'].sum()
                                            st.metric(
                                                "💰 Total Devolvido", 
                                                f"R$ {total_devolvido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                                            )
                                        
                                        with col_met2:
                                            total_faturado = top_devolucao['Vl Net Livro_y'].sum()
                                            st.metric(
                                                "💵 Total Faturado", 
                                                f"R$ {total_faturado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                                            )
                                        
                                        with col_met3:
                                            indice_medio = top_devolucao['Indice_Devolucao_Valor'].mean()
                                            st.metric(
                                                "📊 Índice Médio", 
                                                f"{indice_medio:.2f}%"
                                            )
                                        
                                        with col_met4:
                                            qtd_itens = len(top_devolucao)
                                            st.metric(
                                                "📦 Itens com Devolução", 
                                                f"{qtd_itens}"
                                            )
                                    
                                    else:
                                        st.info(f"📊 Nenhum item com índice de devolução significativo encontrado para {marca}")
                                else:
                                    st.info(f"📊 Nenhum item comum entre faturamento e devolução encontrado para {marca}")
                            else:
                                st.warning(f"⚠️ Dados insuficientes para análise de {marca}")
                else:
                    st.warning("⚠️ Nenhuma marca com dados de devolução e faturamento encontrada")
            else:
                st.warning("⚠️ Colunas necessárias não encontradas nos dados. Verifique se os dados contêm as colunas: Item, Desc Item, Vl Net Livro, Quantidade, Marca")

# CSS específico para cards de devolução
st.markdown("""
<style>
/* CSS específico para cards de devolução */
.card-devolucao {
    background: linear-gradient(135deg, var(--card-color) 0%, var(--card-color-light) 100%);
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    border-left: 4px solid var(--card-color);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.card-devolucao:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.2);
}

.card-devolucao::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255,255,255,0.1);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.card-devolucao:hover::before {
    opacity: 1;
}

.card-title-devolucao {
    color: white;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 12px;
    text-align: center;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    letter-spacing: 0.5px;
}

.card-value-devolucao {
    color: white;
    font-size: 22px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 8px;
    text-shadow: 0 1px 3px rgba(0,0,0,0.4);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.card-subtitle-devolucao {
    color: rgba(255,255,255,0.9);
    font-size: 13px;
    text-align: center;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    background: rgba(0,0,0,0.1);
    padding: 4px 8px;
    border-radius: 6px;
    display: inline-block;
    width: 100%;
    box-sizing: border-box;
}
</style>
""", unsafe_allow_html=True)

# Gráfico de NFs Acumuladas
st.subheader("📈 Notas Fiscais Acumuladas no Mês")

# Calcular NFs acumuladas usando a função do ETL
# Usar faturado_filtrado se existir, senão usar faturado com filtro de receita sim
if 'faturado_filtrado' in locals():
    nfs_acumuladas_geral, nfs_acumuladas_marca = etl_faturamento.calcular_nfs_acumuladas(faturado_filtrado)
else:
    faturado_temp = etl_faturamento.filtrar_receita_sim(faturado.copy())
    nfs_acumuladas_geral, nfs_acumuladas_marca = etl_faturamento.calcular_nfs_acumuladas(faturado_temp)

if not nfs_acumuladas_geral.empty:
    # Criar layout em colunas para os gráficos
    col_nfs_geral, col_nfs_marca = st.columns([1, 1])
    
    with col_nfs_geral:
        # Gráfico de área para NFs acumuladas geral
        fig_nfs_geral = px.area(
            nfs_acumuladas_geral,
            x='Data',
            y='NFs_Acumuladas_Geral',
            title='NFs Acumuladas no Mês (Geral)',
            labels={'NFs_Acumuladas_Geral': 'NFs Acumuladas', 'Data': 'Data'}
        )
        
        fig_nfs_geral.update_layout(
            xaxis_title='Data',
            yaxis_title='NFs Acumuladas',
            hovermode='x unified'
        )
        
        fig_nfs_geral.update_traces(
            fill='tonexty',
            fillcolor='rgba(0, 100, 200, 0.3)',
            line=dict(color='rgb(0, 100, 200)', width=2)
        )
        
        st.plotly_chart(fig_nfs_geral, use_container_width=True, key="nfs_acumuladas_geral")
    
    with col_nfs_marca:
        # Gráfico de área para NFs acumuladas por marca
        if not nfs_acumuladas_marca.empty:
            # Obter cores padronizadas das marcas
            cores_marca = etl_faturamento.obter_cores_marca()
            
            fig_nfs_marca = px.area(
                nfs_acumuladas_marca,
                x='Data',
                y='NFs_Acumuladas_Por_Marca',
                color='Marca',
                title='NFs Acumuladas no Mês por Marca',
                labels={'NFs_Acumuladas_Por_Marca': 'NFs Acumuladas', 'Data': 'Data'},
                color_discrete_map=cores_marca
            )
            
            fig_nfs_marca.update_layout(
                xaxis_title='Data',
                yaxis_title='NFs Acumuladas',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_nfs_marca, use_container_width=True, key="nfs_acumuladas_marca")
        else:
            st.info("📅 Nenhum dado disponível para NFs acumuladas por marca.")
    
    with st.expander("📋 Detalhes das NFs Acumuladas", expanded=False):
        # Mostrar tabela com os dados acumulados
        # st.subheader("📋 Detalhes das NFs Acumuladas")  # Substituído pelo título do expander
        
        # Criar tabela combinada
        tabela_combinada = nfs_acumuladas_geral[['Data', 'NFs_Dia', 'NFs_Acumuladas_Geral']].copy()
        tabela_combinada.columns = ['Data', 'NFs do Dia', 'NFs Acumuladas']
        
        # Formatar valores
        tabela_combinada['NFs do Dia'] = tabela_combinada['NFs do Dia'].apply(lambda x: formatar_valor_seguro(x, 'number'))
        tabela_combinada['NFs Acumuladas'] = tabela_combinada['NFs Acumuladas'].apply(lambda x: formatar_valor_seguro(x, 'number'))
        
        st.dataframe(tabela_combinada, use_container_width=True, hide_index=True)

# ============================================================================
# CURVA ABC DE FATURAMENTO POR ITEM POR MARCA
# ============================================================================

# Colocar toda a Curva ABC em uma aba principal, e as marcas como sub-abas

# Ajuste: Corrige a chamada de formatar_titulo_marcas e melhora a estrutura das abas

# Corrige a chamada de formatar_titulo_marcas (removendo vírgula extra e argumentos corretos)
aba_curva_abc, aba_top_itens = st.tabs([
    formatar_titulo_marcas("📈 Curva ABC de Faturamento por Item por Marca", marcas_selecionadas, marcas_disponiveis),
    formatar_titulo_marcas("📊 Top Itens Faturados", marcas_selecionadas, marcas_disponiveis)
])

with aba_curva_abc:
    st.subheader("Curva ABC de Faturamento por Item por Marca")

    # Obter marcas disponíveis
    marcas_disponiveis_abc = sorted(faturado['Marca'].dropna().unique())

    # Criar sub-abas para cada marca
    subtabs_abc = st.tabs([f"🏷️ {marca}" for marca in marcas_disponiveis_abc])

    def classificar_abc(percentual_acumulado):
        if percentual_acumulado <= 80:
            return 'A'
        elif percentual_acumulado <= 95:
            return 'B'
        else:
            return 'C'

    for idx, marca in enumerate(marcas_disponiveis_abc):
        with subtabs_abc[idx]:
            st.subheader(f"📊 Curva ABC - {marca}")
            
            # Filtrar dados da marca
            faturado_marca = faturado[faturado['Marca'] == marca].copy()
            
            if len(faturado_marca) > 0:
                # Calcular faturamento por item (Desc Item)
                faturamento_por_item = faturado_marca.groupby('Desc Item')['Vl Net Livro'].sum().reset_index()
                faturamento_por_item = faturamento_por_item.sort_values('Vl Net Livro', ascending=False)
                
                # Calcular percentual acumulado
                total_faturamento_marca = faturamento_por_item['Vl Net Livro'].sum()
                faturamento_por_item['Percentual'] = (faturamento_por_item['Vl Net Livro'] / total_faturamento_marca * 100).round(2)
                faturamento_por_item['Percentual_Acumulado'] = faturamento_por_item['Percentual'].cumsum()
                
                # Classificar em categorias ABC
                faturamento_por_item['Classificacao_ABC'] = faturamento_por_item['Percentual_Acumulado'].apply(classificar_abc)
                
                # Formatar valores para exibição
                faturamento_por_item['Valor_Formatado'] = faturamento_por_item['Vl Net Livro'].apply(
                    lambda x: formatar_valor_seguro(x, "currency")
                )
                
                # Separar por classes ABC e pegar top 10 de cada
                classe_a = faturamento_por_item[faturamento_por_item['Classificacao_ABC'] == 'A'].head(10)
                classe_b = faturamento_por_item[faturamento_por_item['Classificacao_ABC'] == 'B'].head(10)
                classe_c = faturamento_por_item[faturamento_por_item['Classificacao_ABC'] == 'C'].head(10)
                
                # Combinar os top 10 de cada classe
                top_10_por_classe = pd.concat([classe_a, classe_b, classe_c]).reset_index(drop=True)
                
                # Criar gráfico da curva ABC apenas com top 10 de cada classe
                fig_abc_marca = go.Figure()
                
                # Adicionar barras de faturamento
                fig_abc_marca.add_trace(go.Bar(
                    x=top_10_por_classe['Desc Item'],
                    y=top_10_por_classe['Vl Net Livro'],
                    name='Faturamento',
                    marker_color=['#1f77b4' if cat == 'A' else '#ff7f0e' if cat == 'B' else '#2ca02c' 
                                  for cat in top_10_por_classe['Classificacao_ABC']],
                    text=top_10_por_classe['Valor_Formatado'],
                    textposition='outside'
                ))
                
                # Adicionar linha de percentual acumulado
                fig_abc_marca.add_trace(go.Scatter(
                    x=top_10_por_classe['Desc Item'],
                    y=top_10_por_classe['Percentual_Acumulado'],
                    mode='lines+markers',
                    name='% Acumulado',
                    yaxis='y2',
                    line=dict(color='red', width=3),
                    marker=dict(size=8)
                ))
                
                # Configurar layout
                fig_abc_marca.update_layout(
                    title=f'📈 Top 10 Itens por Classe ABC - {marca}',
                    xaxis_title='Item',
                    yaxis_title='Faturamento (R$)',
                    yaxis2=dict(
                        title='Percentual Acumulado (%)',
                        overlaying='y',
                        side='right',
                        range=[0, 100]
                    ),
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    height=500,
                    xaxis=dict(tickangle=45)
                )
                
                # Adicionar linhas de referência para classificação ABC
                fig_abc_marca.add_hline(y=80, line_dash="dash", line_color="red", 
                                      annotation_text="80% - Classe A", annotation_position="top right")
                fig_abc_marca.add_hline(y=95, line_dash="dash", line_color="orange", 
                                      annotation_text="95% - Classe B", annotation_position="top right")
                
                st.plotly_chart(fig_abc_marca, use_container_width=True)
                
                # Mostrar tabela de classificação ABC (apenas top 10 de cada classe) em expander
                with st.expander(f"📋 Top 10 Itens por Classe ABC - {marca}", expanded=False):
                    # Preparar dados para exibição (usando top_10_por_classe)
                    df_abc_exibicao = top_10_por_classe[['Desc Item', 'Valor_Formatado', 'Percentual', 'Percentual_Acumulado', 'Classificacao_ABC']].copy()
                    df_abc_exibicao.columns = ['Item', 'Faturamento', '% Individual', '% Acumulado', 'Classificação']
                    
                    # Formatar percentuais
                    df_abc_exibicao['% Individual'] = df_abc_exibicao['% Individual'].apply(lambda x: f"{x:.1f}%")
                    df_abc_exibicao['% Acumulado'] = df_abc_exibicao['% Acumulado'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(df_abc_exibicao, use_container_width=True, hide_index=True)
                
                # Resumo por classificação ABC (top 10 de cada classe)
                st.subheader(f"📊 Resumo Top 10 por Classe ABC - {marca}")
                
                resumo_abc_marca = top_10_por_classe.groupby('Classificacao_ABC').agg({
                    'Desc Item': 'count',
                    'Vl Net Livro': 'sum',
                    'Percentual': 'sum'
                }).reset_index()
                
                resumo_abc_marca.columns = ['Classificação', 'Qtd Itens (Top 10)', 'Faturamento Total', '% do Total']
                resumo_abc_marca['Faturamento Total Formatado'] = resumo_abc_marca['Faturamento Total'].apply(
                    lambda x: formatar_valor_seguro(x, "currency")
                )
                resumo_abc_marca['% do Total'] = resumo_abc_marca['% do Total'].apply(lambda x: f"{x:.1f}%")
                
                # Exibir resumo
                df_resumo_abc_marca = resumo_abc_marca[['Classificação', 'Qtd Itens (Top 10)', 'Faturamento Total Formatado', '% do Total']].copy()
                df_resumo_abc_marca.columns = ['Classificação', 'Qtd Itens (Top 10)', 'Faturamento Total', '% do Total']
                
                st.dataframe(df_resumo_abc_marca, use_container_width=True, hide_index=True)
                
                # Mostrar informações adicionais
                total_itens_marca = len(faturamento_por_item)
                total_itens_top10 = len(top_10_por_classe)
                st.info(f"📊 **Total de itens da marca:** {total_itens_marca} | **Itens exibidos (Top 10 por classe):** {total_itens_top10}")
                
            else:
                st.warning(f"⚠️ Nenhum dado encontrado para a marca {marca}")

    # Interpretação da curva ABC
    st.subheader("💡 Interpretação da Curva ABC")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("""
        **🔵 Classe A (0-80%)**
        - Itens de maior importância
        - Foco principal de gestão
        - Controle rigoroso necessário
        """)

    with col2:
        st.info("""
        **🟠 Classe B (80-95%)**
        - Itens de importância média
        - Controle moderado
        - Potencial de crescimento
        """)

    with col3:
        st.info("""
        **🟢 Classe C (95-100%)**
        - Itens de menor importância
        - Controle simplificado
        - Análise de viabilidade
        """)

with aba_top_itens:
    # Título já formatado na aba
    st.subheader(formatar_titulo_marcas("📊 Top Itens Faturados", marcas_selecionadas, marcas_disponiveis))

    # 🧼 Garantir que o Item está como string
    faturado["Item"] = faturado["Item"].astype(str)
    # -------------------------------
    # Top 10 SKUs mais Faturados (Geral)
    # -------------------------------
    df_top_skus = faturado.groupby("Item")["Quantidade"].sum().reset_index()
    df_top_skus_sorted = df_top_skus.sort_values(by="Quantidade", ascending=False)
    df_top_10_skus = df_top_skus_sorted.head(10)

    fig_top_10_skus = px.bar(
        df_top_10_skus,
        x="Item",
        y="Quantidade",
        text="Quantidade",
        title="🔥 Top 10 SKUs Mais Faturados (Geral)",
        labels={"Quantidade": "Quantidade Faturada", "Item": "SKU"},
        color="Item",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )

    fig_top_10_skus.update_traces(texttemplate="%{y:.0f}", textposition="outside")

    # -------------------------------
    # SKU Mais Faturado por Marca
    # -------------------------------
    df_sku_marca = faturado.groupby(["Marca", "Item"])["Quantidade"].sum().reset_index()
    df_top_skus_por_marca = df_sku_marca.loc[
        df_sku_marca.groupby("Marca")["Quantidade"].idxmax()
    ]

    fig_top_sku_marca = px.bar(
        df_top_skus_por_marca,
        x="Marca",
        y="Quantidade",
        text="Item",
        color="Marca",
        title="🏆 SKU Mais Faturado por Marca",
        labels={"Quantidade": "Quantidade Faturada", "Marca": "Marca"},
        color_discrete_sequence=px.colors.qualitative.Set1,
    )

    fig_top_sku_marca.update_traces(texttemplate="%{y:.0f}", textposition="outside")

    # -------------------------------
    # Top 5 SKUs por Marca (com Facet)
    # -------------------------------
    df_top_5_skus_por_marca = (
        df_sku_marca.groupby("Marca")
        .apply(lambda x: x.nlargest(5, "Quantidade"))
        .reset_index(drop=True)
    )

    fig_top_5_por_marca = px.bar(
        df_top_5_skus_por_marca,
        x="Item",
        y="Quantidade",
        color="Marca",
        facet_col="Marca",
        title="📊 Top 5 SKUs por Marca",
        labels={"Quantidade": "Quantidade Faturada", "Item": "SKU"},
        text="Quantidade",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )

    fig_top_5_por_marca.update_traces(texttemplate="%{y:.0f}", textposition="outside")
    fig_top_5_por_marca.update_layout(showlegend=False)

    # -------------------------------
    # Exibir no Streamlit
    # -------------------------------
    tab1, tab2, tab3 = st.tabs(
        [
            "Top 10 por Marca",
            "Top 10 Geral",
            "SKU Mais Faturado por Marca",
        ]
    )

    with tab1:
        # 🔍 Filtro de Seleção de Marca na aba col3
        marcas_disponiveis = sorted(faturado["Marca"].dropna().unique())
        marca_selecionada = st.selectbox("Escolha a Marca", options=marcas_disponiveis)

        # 🧼 Filtrar os dados com base na marca selecionada
        df_faturado_filtrado_marca = faturado[
            faturado["Marca"] == marca_selecionada
        ].copy()

        # 🔢 Converter SKU para string (para evitar confusão no gráfico)
        df_faturado_filtrado_marca["Item"] = df_faturado_filtrado_marca["Item"].astype(str)

        # 📊 Agrupar os dados filtrados por SKU e somar as quantidades faturadas
        df_top_skus_marca = (
            df_faturado_filtrado_marca.groupby(["Item", "Desc Item"])["Quantidade"]
            .sum()
            .reset_index()
        )

        # 📈 Ordenar os SKUs pela quantidade faturada de forma decrescente
        df_top_skus_marca_sorted = df_top_skus_marca.sort_values(
            by="Quantidade", ascending=False
        )

        # 🥇 Selecionar os 10 SKUs mais faturados
        df_top_10_skus_marca = df_top_skus_marca_sorted.head(10)

        # 🎨 Gráfico de barras dos Top 10 SKUs da Marca Selecionada
        fig_top_10_skus_marca = px.bar(
            df_top_10_skus_marca,
            x="Desc Item",
            y="Quantidade",
            title=f"📊 Top 10 SKUs mais Faturados - Marca: {marca_selecionada}",
            labels={"Quantidade": "Quantidade Faturada", "Desc Item": "Descrição do Item"},
            color="Item",
            color_discrete_sequence=px.colors.qualitative.Set1,
            text_auto=True,
        )

        fig_top_10_skus_marca.update_traces(texttemplate="%{y:.0f}")

        st.plotly_chart(fig_top_10_skus_marca, use_container_width=True)

    with tab2:
        st.write(
            "📊 **Top 10 SKUs mais faturados em quantidade em todo o período selecionado**"
        )
        st.plotly_chart(fig_top_10_skus, use_container_width=True)

        # Mostrar tabela detalhada
        st.subheader("📋 Detalhes dos Top 10 SKUs")
        # Adicionar descrição dos itens
        df_top_10_com_desc = df_top_10_skus.merge(
            faturado[["Item", "Desc Item"]].drop_duplicates(), on="Item", how="left"
        )

        df_top_10_com_desc = df_top_10_com_desc[
            ["Item", "Desc Item", "Quantidade"]
        ].rename(
            columns={
                "Item": "SKU",
                "Desc Item": "Descrição",
                "Quantidade": "Quantidade Total",
            }
        )

        # Formatar quantidade
        df_top_10_com_desc["Quantidade Total"] = df_top_10_com_desc[
            "Quantidade Total"
        ].apply(lambda x: formatar_valor_seguro(x, "number"))

        st.dataframe(df_top_10_com_desc, use_container_width=True)

    with tab3:
        st.write("🏆 **SKU com maior quantidade faturada em cada marca**")
        st.plotly_chart(fig_top_sku_marca, use_container_width=True)

        # Mostrar tabela detalhada
        st.subheader("📋 Detalhes por Marca")
        # Adicionar descrição dos itens
        df_top_marca_com_desc = df_top_skus_por_marca.merge(
            faturado[["Item", "Desc Item"]].drop_duplicates(), on="Item", how="left"
        )

        df_top_marca_com_desc = df_top_marca_com_desc[
            ["Marca", "Item", "Desc Item", "Quantidade"]
        ].rename(
            columns={
                "Marca": "Marca",
                "Item": "SKU",
                "Desc Item": "Descrição",
                "Quantidade": "Quantidade",
            }
        )

        # Formatar quantidade
        df_top_marca_com_desc["Quantidade"] = df_top_marca_com_desc["Quantidade"].apply(
            lambda x: formatar_valor_seguro(x, "number")
        )

        st.dataframe(df_top_marca_com_desc, use_container_width=True)
    
st.divider()
st.title("🔍 Busca Avançada")
# Filtro de Canal de Venda

# --- Novo bloco de busca ---
col_busca1, col_busca2, col_busca3 = st.columns(3)

with col_busca1:
    busca_nf = st.text_input("🔍 Buscar por Nota Fiscal", value="", key="busca_nf")

with col_busca2:
    busca_pedcli = st.text_input("🔍 Buscar por Pedido Cliente", value="", key="busca_pedcli")

with col_busca3:
    busca_razao = st.text_input("🔍 Buscar por Razão Social", value="", key="busca_razao")

canais_disponiveis = sorted(faturado['Canal Venda Cliente'].dropna().unique()) if 'Canal Venda Cliente' in faturado.columns else []
canal_selecionado = st.multiselect(
    "Filtrar Canal de Venda:",
    options=canais_disponiveis,
    default=canais_disponiveis,
    key="canal_venda_filtrado",
    help="Selecione um ou mais canais de venda para exibir no dataframe."
)

# Aplicar filtro ao DataFrame e remover Notas Fiscais duplicadas SEMPRE
if 'Canal Venda Cliente' in faturado.columns and canal_selecionado:
    faturado_filtrado_can = faturado[faturado['Canal Venda Cliente'].isin(canal_selecionado)].copy()
else:
    faturado_filtrado_can = faturado.copy()

# Aplicar filtros de busca
if busca_nf:
    faturado_filtrado_can = faturado_filtrado_can[
        faturado_filtrado_can['Nota Fiscal'].astype(str).str.contains(busca_nf, case=False, na=False)
    ]
if busca_pedcli:
    faturado_filtrado_can = faturado_filtrado_can[
        faturado_filtrado_can['Ped Cliente'].astype(str).str.contains(busca_pedcli, case=False, na=False)
    ]
if busca_razao:
    faturado_filtrado_can = faturado_filtrado_can[
        faturado_filtrado_can['Razao Social'].astype(str).str.contains(busca_razao, case=False, na=False)
    ]

# Remover duplicatas de Nota Fiscal, mantendo apenas a primeira ocorrência
if 'Nota Fiscal' in faturado_filtrado_can.columns:
    faturado_filtrado_can = faturado_filtrado_can.drop_duplicates(subset=['Nota Fiscal'])

st.dataframe(faturado_filtrado_can, use_container_width=True)


