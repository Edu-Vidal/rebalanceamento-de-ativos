POSITIVE_INFINITY = float('inf')

def validar_entradas(ativos_atuais, percentuais_alvo):
    """
    Valida as entradas da função de rebalanceamento.
    
    Args:
        ativos_atuais (dict): Dicionário com ativos e seus valores atuais
        percentuais_alvo (dict): Dicionário com ativos e percentuais alvo
    
    Raises:
        ValueError: Se as validações falharem
    """
    if not ativos_atuais or not percentuais_alvo:
        raise ValueError("Ativos atuais e percentuais alvo não podem estar vazios")
    
    # Verificar se os ativos coincidem
    ativos_atual_set = set(ativos_atuais.keys())
    ativos_alvo_set = set(percentuais_alvo.keys())
    
    if ativos_atual_set != ativos_alvo_set:
        raise ValueError("Os ativos em 'ativos_atuais' devem coincidir com os em 'percentuais_alvo'")
    
    # Verificar se a soma dos percentuais alvo é 100%
    soma_percentuais = sum(percentuais_alvo.values())
    if abs(soma_percentuais - 100) > 0.01:  # Tolerância para erros de ponto flutuante
        raise ValueError(f"A soma dos percentuais alvo deve ser 100%. Atual: {soma_percentuais}%")


def calcular_percentuais_atuais(ativos_atuais):
    """
    Calcula os percentuais atuais de cada ativo na carteira.
    
    Args:
        ativos_atuais (dict): Dicionário com ativos e seus valores atuais
    
    Returns:
        dict: Dicionário com percentuais atuais de cada ativo
    """
    patrimonio_atual = sum(ativos_atuais.values())
    percentuais_atuais = {}
    
    for ativo, valor in ativos_atuais.items():
        percentuais_atuais[ativo] = (valor / patrimonio_atual) * 100 if patrimonio_atual > 0 else 0
    
    return percentuais_atuais


def validar_ativos_fixos(ativos_atuais, ativos_fixos, percentuais_alvo):
    """
    Valida se é possível manter os ativos fixos com os percentuais desejados.
    
    Args:
        ativos_atuais (dict): Valores atuais dos ativos
        ativos_fixos (list): Lista de ativos que devem ser mantidos fixos
        percentuais_alvo (dict): Percentuais alvo de cada ativo
    
    Returns:
        tuple: (is_valid, error_message, patrimonio_disponivel_percentual)
    """
    if not ativos_fixos:
        return True, None, 100.0
    
    # Verificar se todos os ativos fixos existem
    for ativo in ativos_fixos:
        if ativo not in ativos_atuais:
            return False, f"Ativo fixo '{ativo}' não encontrado nos ativos atuais", 0
        if ativo not in percentuais_alvo:
            return False, f"Ativo fixo '{ativo}' não tem percentual alvo definido", 0
    
    patrimonio_total = sum(ativos_atuais.values())
    
    # Calcular percentual ocupado pelos ativos fixos
    valor_ativos_fixos = sum(ativos_atuais[ativo] for ativo in ativos_fixos)
    percentual_ativos_fixos = (valor_ativos_fixos / patrimonio_total) * 100 if patrimonio_total > 0 else 0
    
    # Calcular percentual alvo dos ativos fixos
    percentual_alvo_fixos = sum(percentuais_alvo[ativo] for ativo in ativos_fixos)
    
    # Verificar se os percentuais dos ativos fixos são compatíveis
    if abs(percentual_ativos_fixos - percentual_alvo_fixos) > 0.01:
        return False, (f"Incompatibilidade: ativos fixos ocupam {percentual_ativos_fixos:.2f}% "
                      f"mas o alvo é {percentual_alvo_fixos:.2f}%"), 0
    
    # Calcular percentual disponível para os outros ativos
    percentual_disponivel = 100 - percentual_alvo_fixos
    
    # Verificar se sobra espaço para os outros ativos
    ativos_variaveis = [ativo for ativo in ativos_atuais.keys() if ativo not in ativos_fixos]
    percentual_alvo_variaveis = sum(percentuais_alvo[ativo] for ativo in ativos_variaveis)
    
    if abs(percentual_alvo_variaveis - percentual_disponivel) > 0.01:
        return False, (f"Incompatibilidade: ativos variáveis precisam de {percentual_alvo_variaveis:.2f}% "
                      f"mas só há {percentual_disponivel:.2f}% disponível"), 0
    
    return True, None, percentual_disponivel


def calcular_rebalanceamento_otimizado(ativos_atuais, percentuais_alvo, valor_aporte_disponivel=POSITIVE_INFINITY, ativos_fixos=None):
    """
    Calcula o rebalanceamento otimizado para atingir os percentuais alvo com o menor aporte possível.
    Permite vendas de ativos não fixos para reduzir a necessidade de aportes externos.
    
    Args:
        ativos_atuais (dict): Valores atuais dos ativos
        percentuais_alvo (dict): Percentuais alvo de cada ativo (0-100)
        valor_aporte_disponivel (float): Valor máximo disponível para aporte externo
        ativos_fixos (list): Lista de ativos que devem ser mantidos fixos (opcional)
    
    Returns:
        dict: {
            'patrimonio_alvo': float,
            'aporte_necessario': float,
            'acoes_por_ativo': dict,  # +aporte, -venda, 0=fixo
            'valores_finais': dict,
            'percentuais_finais': dict,
            'total_vendas': float,
            'total_aportes_internos': float,
            'viavel': bool,
            'motivo_inviabilidade': str
        }
    """
    # Validar entradas
    validar_entradas(ativos_atuais, percentuais_alvo)
    
    patrimonio_atual = sum(ativos_atuais.values())
    ativos_fixos = ativos_fixos or []
    
    # Validar ativos fixos
    if ativos_fixos:
        is_valid, error_msg, _ = validar_ativos_fixos(ativos_atuais, ativos_fixos, percentuais_alvo)
        if not is_valid:
            return {
                'viavel': False,
                'motivo_inviabilidade': f"Classe de ativos fixos incompatíveis: {error_msg}",
                'patrimonio_alvo': 0,
                'aporte_necessario': 0,
                'acoes_por_ativo': {},
                'valores_finais': {},
                'percentuais_finais': {},
                'total_vendas': 0,
                'total_aportes_internos': 0
            }
    
    print(f"REBALANCEAMENTO OTIMIZADO")
    print("=" * 45)
    print(f"Patrimônio atual: R$ {patrimonio_atual:,.2f}")
    if valor_aporte_disponivel != POSITIVE_INFINITY:
        print(f"Aporte disponível: R$ {valor_aporte_disponivel:,.2f}")
    if ativos_fixos:
        print(f"Classe de ativos fixos: {', '.join(ativos_fixos)}")
    print("Estratégia: Vendas + aportes otimizados")
    print()
    
    # 1. Calcular patrimônio alvo mínimo
    patrimonio_alvo = _calcular_patrimonio_alvo_minimo(ativos_atuais, percentuais_alvo, ativos_fixos)
    
    # 2. Calcular valores alvo para cada ativo
    valores_alvo = {}
    for ativo, perc_alvo in percentuais_alvo.items():
        if ativo in ativos_fixos:
            valores_alvo[ativo] = ativos_atuais[ativo]  # Manter fixo
        else:
            valores_alvo[ativo] = (perc_alvo / 100) * patrimonio_alvo
    
    # 3. Calcular ações necessárias
    acoes_por_ativo = {}
    total_aportes_internos = 0
    total_vendas = 0
    
    for ativo, valor_atual in ativos_atuais.items():
        valor_alvo = valores_alvo[ativo]
        
        if ativo in ativos_fixos:
            acoes_por_ativo[ativo] = 0  # Manter fixo
        elif valor_alvo > valor_atual:
            # Precisa de aporte
            aporte_necessario = valor_alvo - valor_atual
            acoes_por_ativo[ativo] = aporte_necessario
            total_aportes_internos += aporte_necessario
        elif valor_alvo < valor_atual:
            # Pode ser vendido
            venda_possivel = valor_atual - valor_alvo
            acoes_por_ativo[ativo] = -venda_possivel
            total_vendas += venda_possivel
        else:
            acoes_por_ativo[ativo] = 0  # Já no alvo
    
    # 4. Verificar viabilidade
    aporte_necessario = total_aportes_internos - total_vendas
    
    if valor_aporte_disponivel != POSITIVE_INFINITY and aporte_necessario > valor_aporte_disponivel:
        return {
            'viavel': False,
            'motivo_inviabilidade': f"Aporte necessário (R$ {aporte_necessario:,.2f}) excede disponível (R$ {valor_aporte_disponivel:,.2f})",
            'patrimonio_alvo': patrimonio_alvo,
            'aporte_necessario': aporte_necessario,
            'acoes_por_ativo': acoes_por_ativo,
            'valores_finais': valores_alvo,
            'percentuais_finais': {ativo: (valor / patrimonio_alvo) * 100 for ativo, valor in valores_alvo.items()},
            'total_vendas': total_vendas,
            'total_aportes_internos': total_aportes_internos
        }
    
    # 5. Calcular percentuais finais
    percentuais_finais = {}
    for ativo, valor_final in valores_alvo.items():
        percentuais_finais[ativo] = (valor_final / patrimonio_alvo) * 100
    
    # 6. Exibir resultados
    _exibir_resultado_otimizado(ativos_atuais, percentuais_alvo, valores_alvo, 
                               acoes_por_ativo, percentuais_finais, patrimonio_alvo,
                               aporte_necessario, total_vendas, total_aportes_internos, ativos_fixos)
    
    return {
        'viavel': True,
        'motivo_inviabilidade': None,
        'patrimonio_alvo': patrimonio_alvo,
        'aporte_necessario': max(0, aporte_necessario),  # Não pode ser negativo
        'acoes_por_ativo': acoes_por_ativo,
        'valores_finais': valores_alvo,
        'percentuais_finais': percentuais_finais,
        'total_vendas': total_vendas,
        'total_aportes_internos': total_aportes_internos
    }


def _calcular_patrimonio_alvo_minimo(ativos_atuais, percentuais_alvo, ativos_fixos):
    """
    Calcula o patrimônio alvo mínimo otimizado, considerando vendas e compras
    para encontrar a solução mais próxima do patrimônio atual.
    """
    patrimonio_atual = sum(ativos_atuais.values())
    ativos_fixos = ativos_fixos or []
    
    # 1. Se há ativos fixos, eles definem restrições rígidas
    if ativos_fixos:
        patrimonio_minimo_fixos = 0
        for ativo in ativos_fixos:
            valor_atual = ativos_atuais[ativo]
            perc_alvo = percentuais_alvo[ativo]
            patrimonio_necessario = valor_atual / (perc_alvo / 100)
            patrimonio_minimo_fixos = max(patrimonio_minimo_fixos, patrimonio_necessario)
        return patrimonio_minimo_fixos
    
    # 2. Se não há ativos fixos, otimizar para o menor patrimônio possível
    # Testar diferentes cenários de patrimônio alvo
    
    # Cenário 1: Patrimônio atual (sem aportes externos)
    if _verificar_viabilidade_patrimonio(ativos_atuais, percentuais_alvo, patrimonio_atual):
        return patrimonio_atual
    
    # Cenário 2: Para cada ativo, calcular o patrimônio se ele não for vendido
    candidatos_patrimonio = []
    
    for ativo, valor_atual in ativos_atuais.items():
        perc_alvo = percentuais_alvo[ativo]
        patrimonio_candidato = valor_atual / (perc_alvo / 100)
        
        # Verificar se este patrimônio candidato é viável para todos os ativos
        if _verificar_viabilidade_patrimonio(ativos_atuais, percentuais_alvo, patrimonio_candidato):
            candidatos_patrimonio.append(patrimonio_candidato)
    
    # Escolher o menor patrimônio viável
    if candidatos_patrimonio:
        return min(candidatos_patrimonio)
    
    # Fallback: se nenhum cenário individual funciona, usar o maior necessário
    patrimonios_necessarios = []
    for ativo, valor_atual in ativos_atuais.items():
        perc_alvo = percentuais_alvo[ativo]
        patrimonio_necessario = valor_atual / (perc_alvo / 100)
        patrimonios_necessarios.append(patrimonio_necessario)
    
    return min(patrimonios_necessarios)


def _verificar_viabilidade_patrimonio(ativos_atuais, percentuais_alvo, patrimonio_teste):
    """
    Verifica se é possível atingir os percentuais alvo com o patrimônio dado,
    considerando que ativos só podem ser vendidos (não podem ter valor aumentado sem aporte).
    """
    total_vendas_possiveis = 0
    total_compras_necessarias = 0
    
    for ativo, valor_atual in ativos_atuais.items():
        perc_alvo = percentuais_alvo[ativo]
        valor_alvo = (perc_alvo / 100) * patrimonio_teste
        
        if valor_alvo > valor_atual:
            # Precisa comprar (aporte necessário)
            total_compras_necessarias += (valor_alvo - valor_atual)
        elif valor_alvo < valor_atual:
            # Pode vender
            total_vendas_possiveis += (valor_atual - valor_alvo)
        # Se valor_alvo == valor_atual, não há ação necessária
    
    # É viável se as vendas cobrem as compras (sem aporte externo)
    return total_vendas_possiveis >= total_compras_necessarias


def _exibir_resultado_otimizado(ativos_atuais, percentuais_alvo, valores_alvo, 
                               acoes_por_ativo, percentuais_finais, patrimonio_alvo,
                               aporte_necessario, total_vendas, total_aportes_internos, ativos_fixos):
    """
    Exibe os resultados do rebalanceamento otimizado de forma organizada.
    """
    percentuais_atuais = calcular_percentuais_atuais(ativos_atuais)
    
    print(f"{'Ativo':<15} {'Atual':<12} {'%Atual':<8} {'%Alvo':<8} {'Alvo':<12} {'%Final':<8} {'Ação':<15} {'Status':<10}")
    print("-" * 110)
    
    for ativo in ativos_atuais.keys():
        valor_atual = ativos_atuais[ativo]
        percentual_atual = percentuais_atuais[ativo]
        percentual_alvo = percentuais_alvo[ativo]
        valor_alvo = valores_alvo[ativo]
        percentual_final = percentuais_finais[ativo]
        acao = acoes_por_ativo[ativo]
        
        if ativo in ativos_fixos:
            acao_str = "FIXO"
            status = "🔒 FIXO"
        elif acao > 0:
            acao_str = f"Comprar R$ {acao:,.2f}"
            status = "📈 COMPRA"
        elif acao < 0:
            acao_str = f"Vender R$ {abs(acao):,.2f}"
            status = "📉 VENDA"
        else:
            acao_str = "Manter"
            status = "✅ OK"
        
        print(f"{ativo:<15} R$ {valor_atual:<10.2f} {percentual_atual:<7.1f}% {percentual_alvo:<7.1f}% "
              f"R$ {valor_alvo:<10.2f} {percentual_final:<7.1f}% {acao_str:<15} {status}")
    
    print("-" * 110)
    print(f"Patrimônio alvo: R$ {patrimonio_alvo:,.2f}")
    print(f"Total de vendas internas: R$ {total_vendas:,.2f}")
    print(f"Total de compras internas: R$ {total_aportes_internos:,.2f}")
    print(f"Aporte externo necessário: R$ {max(0, aporte_necessario):,.2f}")
    
    if aporte_necessario <= 0:
        print("✅ Rebalanceamento possível apenas com vendas internas!")
    else:
        print(f"💰 Aporte externo de R$ {aporte_necessario:,.2f} necessário")


def calcular_rebalanceamento_otimizado_silencioso(ativos_atuais, percentuais_alvo, valor_aporte_disponivel=POSITIVE_INFINITY, ativos_fixos=None):
    """
    Versão silenciosa da função calcular_rebalanceamento_otimizado (sem prints).
    Calcula o rebalanceamento otimizado para atingir os percentuais alvo com o menor aporte possível.
    
    Args:
        ativos_atuais (dict): Valores atuais dos ativos
        percentuais_alvo (dict): Percentuais alvo de cada ativo (0-100)
        valor_aporte_disponivel (float): Valor máximo disponível para aporte externo
        ativos_fixos (list): Lista de ativos que devem ser mantidos fixos (opcional)
    
    Returns:
        dict: Resultado do cálculo com informações detalhadas
    """
    # Validar entradas
    validar_entradas(ativos_atuais, percentuais_alvo)
    
    patrimonio_atual = sum(ativos_atuais.values())
    ativos_fixos = ativos_fixos or []
    
    # Validar ativos fixos
    if ativos_fixos:
        is_valid, error_msg, _ = validar_ativos_fixos(ativos_atuais, ativos_fixos, percentuais_alvo)
        if not is_valid:
            return {
                'viavel': False,
                'motivo_inviabilidade': f"Classes incompatíveis: {error_msg}",
                'patrimonio_atual': patrimonio_atual,
                'patrimonio_alvo': 0,
                'aporte_necessario': 0,
                'acoes_por_ativo': {},
                'valores_finais': {},
                'percentuais_atuais': {},
                'percentuais_finais': {},
                'total_vendas': 0,
                'total_aportes_internos': 0
            }
    
    # 1. Calcular patrimônio alvo mínimo
    patrimonio_alvo = _calcular_patrimonio_alvo_minimo(ativos_atuais, percentuais_alvo, ativos_fixos)
    
    # 2. Calcular valores alvo para cada ativo
    valores_alvo = {}
    for ativo, perc_alvo in percentuais_alvo.items():
        if ativo in ativos_fixos:
            valores_alvo[ativo] = ativos_atuais[ativo]  # Manter fixo
        else:
            valores_alvo[ativo] = (perc_alvo / 100) * patrimonio_alvo
    
    # 3. Calcular ações necessárias
    acoes_por_ativo = {}
    total_aportes_internos = 0
    total_vendas = 0
    
    for ativo, valor_atual in ativos_atuais.items():
        valor_alvo = valores_alvo[ativo]
        
        if ativo in ativos_fixos:
            acoes_por_ativo[ativo] = 0  # Manter fixo
        elif valor_alvo > valor_atual:
            # Precisa de aporte
            aporte_necessario = valor_alvo - valor_atual
            acoes_por_ativo[ativo] = aporte_necessario
            total_aportes_internos += aporte_necessario
        elif valor_alvo < valor_atual:
            # Pode ser vendido
            venda_possivel = valor_atual - valor_alvo
            acoes_por_ativo[ativo] = -venda_possivel
            total_vendas += venda_possivel
        else:
            acoes_por_ativo[ativo] = 0  # Já no alvo
    
    # 4. Verificar viabilidade
    aporte_necessario = total_aportes_internos - total_vendas
    
    if valor_aporte_disponivel != POSITIVE_INFINITY and aporte_necessario > valor_aporte_disponivel:
        return {
            'viavel': False,
            'motivo_inviabilidade': f"Aporte necessário (R$ {aporte_necessario:,.2f}) excede disponível (R$ {valor_aporte_disponivel:,.2f})",
            'patrimonio_atual': patrimonio_atual,
            'patrimonio_alvo': patrimonio_alvo,
            'aporte_necessario': aporte_necessario,
            'acoes_por_ativo': acoes_por_ativo,
            'valores_finais': valores_alvo,
            'percentuais_atuais': calcular_percentuais_atuais(ativos_atuais),
            'percentuais_finais': {ativo: (valor / patrimonio_alvo) * 100 for ativo, valor in valores_alvo.items()},
            'total_vendas': total_vendas,
            'total_aportes_internos': total_aportes_internos
        }
    
    # 5. Calcular percentuais atuais e finais
    percentuais_atuais = calcular_percentuais_atuais(ativos_atuais)
    percentuais_finais = {}
    for ativo, valor_final in valores_alvo.items():
        percentuais_finais[ativo] = (valor_final / patrimonio_alvo) * 100
    
    return {
        'viavel': True,
        'motivo_inviabilidade': None,
        'patrimonio_atual': patrimonio_atual,
        'patrimonio_alvo': patrimonio_alvo,
        'aporte_necessario': max(0, aporte_necessario),  # Não pode ser negativo
        'acoes_por_ativo': acoes_por_ativo,
        'valores_finais': valores_alvo,
        'percentuais_atuais': percentuais_atuais,
        'percentuais_finais': percentuais_finais,
        'total_vendas': total_vendas,
        'total_aportes_internos': total_aportes_internos
    }


if __name__ == "__main__":
    print("Sistema de Rebalanceamento de Ativos")
    print("="*40)
    print("Função disponível:")
    print("• calcular_rebalanceamento_otimizado()")
    print()
    print("Para acessar a interface web, execute:")
    print("streamlit run app.py")
