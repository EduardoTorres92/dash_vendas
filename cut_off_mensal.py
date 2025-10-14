# Valores de Cut-off por Mês - Dados Históricos Fixos
# Estes valores são usados no faturamento.py para calcular o faturamento líquido
# Unidades: UNIDADE SOROCABA, SAO PAULO, FLORIANOPOLIS, CURITIBA, PORTO ALEGRE

CUT_OFF_MENSAL = {
    "Janeiro": {
        "UNIDADE SOROCABA": 928937.76,
        "UNIDADE SAO PAULO": 716502.83,
        "UNIDADE FLORIANOPOLIS": 86295.05,
        "UNIDADE CURITIBA": 857314.52,
        "UNIDADE PORTO ALEGRE": 0,
        "UNIDADE BRASILIA": 0
    },
    "Fevereiro": {
        "UNIDADE SOROCABA": 997772.84,
        "UNIDADE SAO PAULO": 563921.19,
        "UNIDADE FLORIANOPOLIS": 150464.46,
        "UNIDADE CURITIBA": 113613.27,
        "UNIDADE PORTO ALEGRE": 0,
        "UNIDADE BRASILIA": 0
    },
    "Março": {
        "UNIDADE SOROCABA": 401614.00,
        "UNIDADE SAO PAULO": 365160.54,
        "UNIDADE FLORIANOPOLIS": 764070.96,
        "UNIDADE CURITIBA": 231200.28,
        "UNIDADE PORTO ALEGRE": 0,
        "UNIDADE BRASILIA": 0
    },
    "Abril": {
        "UNIDADE SOROCABA": 1261226.90,
        "UNIDADE SAO PAULO": 519183.19,
        "UNIDADE FLORIANOPOLIS": 140241.08,
        "UNIDADE CURITIBA": 16364.11,
        "UNIDADE PORTO ALEGRE": 57197.98,
        "UNIDADE BRASILIA": 0
    },
    "Maio": {
        "UNIDADE SOROCABA": 2111740.93,
        "UNIDADE SAO PAULO": 162323.81,
        "UNIDADE FLORIANOPOLIS": 83033.94,
        "UNIDADE CURITIBA": 13572.57,
        "UNIDADE PORTO ALEGRE": 35211.17,
        "UNIDADE BRASILIA": 0
    },
    "Junho": {
        "UNIDADE SOROCABA": 1025657.73,
        "UNIDADE SAO PAULO": 392695.43,
        "UNIDADE FLORIANOPOLIS": 123630.95,
        "UNIDADE CURITIBA": 29857.46,
        "UNIDADE PORTO ALEGRE": 119144.57,
        "UNIDADE BRASILIA": 0
    },
    "Julho": {
        "UNIDADE SOROCABA": 261693.01,
        "UNIDADE SAO PAULO": 50551.02,
        "UNIDADE FLORIANOPOLIS": 12868.08,
        "UNIDADE CURITIBA": 6743.91,
        "UNIDADE PORTO ALEGRE": 46447.98,
        "UNIDADE BRASILIA": 0
    },
    "Agosto": {
        "UNIDADE SOROCABA": 1349786.77,
        "UNIDADE SAO PAULO": 282503.04,
        "UNIDADE FLORIANOPOLIS": 76970.98,
        "UNIDADE CURITIBA": 1053663.75,
        "UNIDADE PORTO ALEGRE": 0,
        "UNIDADE BRASILIA": 0
    },
    "Setembro": {
        "UNIDADE SOROCABA": 561144.15,
        "UNIDADE SAO PAULO": 217471.56,
        "UNIDADE FLORIANOPOLIS": 59647.63,
        "UNIDADE CURITIBA": 94171.07,
        "UNIDADE PORTO ALEGRE": 32702.43,
        "UNIDADE BRASILIA": 0
    },
    "Outubro": {
        "UNIDADE SOROCABA": 0,
        "UNIDADE SAO PAULO": 0,
        "UNIDADE FLORIANOPOLIS": 0,
        "UNIDADE CURITIBA": 0,
        "UNIDADE PORTO ALEGRE": 0,
        "UNIDADE BRASILIA": 0
    },
    "Novembro": {
        "UNIDADE SOROCABA": 0,
        "UNIDADE SAO PAULO": 0,
        "UNIDADE FLORIANOPOLIS": 0,
        "UNIDADE CURITIBA": 0,
        "UNIDADE PORTO ALEGRE": 0,
        "UNIDADE BRASILIA": 0
    },
    "Dezembro": {
        "UNIDADE SOROCABA": 0,
        "UNIDADE SAO PAULO": 0,
        "UNIDADE FLORIANOPOLIS": 0,
        "UNIDADE CURITIBA": 0,
        "UNIDADE PORTO ALEGRE": 0,
        "UNIDADE BRASILIA": 0
    }
}

# Função para obter o cut-off de uma unidade em um mês específico
def get_cut_off_mensal(mes, unidade):
    """
    Retorna o valor de cut-off para uma unidade em um mês específico
    
    Args:
        mes (str): Nome do mês (ex: 'Janeiro', 'Agosto')
        unidade (str): Nome da unidade (ex: 'UNIDADE SOROCABA', 'UNIDADE SAO PAULO')
    
    Returns:
        float: Valor do cut-off para a unidade no mês especificado (retorna 0 se não encontrado)
    """
    try:
        return CUT_OFF_MENSAL.get(mes, {}).get(unidade, 0)
    except:
        return 0

# Função para obter o cut-off total de um mês
def get_cut_off_total_mensal(mes):
    """
    Retorna o valor total de cut-off de um mês (soma de todas as unidades)
    
    Args:
        mes (str): Nome do mês (ex: 'Janeiro', 'Agosto')
    
    Returns:
        float: Valor total do cut-off do mês
    """
    try:
        return sum(CUT_OFF_MENSAL.get(mes, {}).values())
    except:
        return 0
