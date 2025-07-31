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


def calcular_valores_alvo(percentuais_alvo, patrimonio_total):
    """
    Calcula os valores alvo para cada ativo baseado no patrimônio total.
    
    Args:
        percentuais_alvo (dict): Dicionário com percentuais alvo de cada ativo
        patrimonio_total (float): Valor total do patrimônio após aporte
    
    Returns:
        dict: Dicionário com valores alvo para cada ativo
    """
    valores_alvo = {}
    for ativo, percentual in percentuais_alvo.items():
        valores_alvo[ativo] = (percentual / 100) * patrimonio_total
    
    return valores_alvo


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


def calcular_valores_alvo_com_fixos(ativos_atuais, percentuais_alvo, patrimonio_total, ativos_fixos=None):
    """
    Calcula os valores alvo considerando ativos que devem ser mantidos fixos.
    
    Args:
        ativos_atuais (dict): Valores atuais dos ativos
        percentuais_alvo (dict): Percentuais alvo de cada ativo
        patrimonio_total (float): Valor total do patrimônio após aporte
        ativos_fixos (list): Lista de ativos que devem ser mantidos fixos (opcional)
    
    Returns:
        dict: Dicionário com valores alvo para cada ativo
    
    Raises:
        ValueError: Se a combinação de ativos fixos e percentuais for inválida
    """
    if not ativos_fixos:
        return calcular_valores_alvo(percentuais_alvo, patrimonio_total)
    
    # Validar se é possível manter os ativos fixos
    is_valid, error_msg, _ = validar_ativos_fixos(ativos_atuais, ativos_fixos, percentuais_alvo)
    if not is_valid:
        raise ValueError(f"Não é possível manter os ativos fixos: {error_msg}")
    
    valores_alvo = {}
    
    # Para ativos fixos, manter o valor atual
    for ativo in ativos_fixos:
        valores_alvo[ativo] = ativos_atuais[ativo]
    
    # Calcular patrimônio disponível para ativos variáveis
    valor_ativos_fixos = sum(ativos_atuais[ativo] for ativo in ativos_fixos)
    patrimonio_disponivel = patrimonio_total - valor_ativos_fixos
    
    # Calcular percentual total dos ativos variáveis
    ativos_variaveis = [ativo for ativo in ativos_atuais.keys() if ativo not in ativos_fixos]
    percentual_total_variaveis = sum(percentuais_alvo[ativo] for ativo in ativos_variaveis)
    
    # Calcular valores alvo para ativos variáveis proporcionalmente
    for ativo in ativos_variaveis:
        proporcao = percentuais_alvo[ativo] / percentual_total_variaveis if percentual_total_variaveis > 0 else 0
        valores_alvo[ativo] = proporcao * patrimonio_disponivel
    
    return valores_alvo


def calcular_acoes_necessarias(ativos_atuais, valores_alvo):
    """
    Calcula as ações necessárias (aportes ou vendas) para cada ativo.
    
    Args:
        ativos_atuais (dict): Dicionário com valores atuais dos ativos
        valores_alvo (dict): Dicionário com valores alvo dos ativos
    
    Returns:
        tuple: (acoes_necessarias, total_aportes, total_vendas)
    """
    acoes_necessarias = {}
    total_aportes = 0
    total_vendas = 0
    
    for ativo in ativos_atuais.keys():
        valor_atual = ativos_atuais[ativo]
        valor_alvo = valores_alvo[ativo]
        diferenca = valor_alvo - valor_atual
        
        acoes_necessarias[ativo] = diferenca
        
        if diferenca > 0:
            total_aportes += diferenca
        elif diferenca < 0:
            total_vendas += abs(diferenca)
    
    return acoes_necessarias, total_aportes, total_vendas


def formatar_acao(diferenca):
    """
    Formata a ação necessária como string para exibição.
    
    Args:
        diferenca (float): Diferença entre valor alvo e atual
    
    Returns:
        str: String formatada da ação necessária
    """
    if diferenca > 0:
        return f"+R$ {diferenca:,.2f}"
    elif diferenca < 0:
        return f"-R$ {abs(diferenca):,.2f}"
    else:
        return "Manter"


def exibir_resumo_patrimonio(patrimonio_atual, valor_aporte_total):
    """
    Exibe resumo do patrimônio atual e após aporte.
    
    Args:
        patrimonio_atual (float): Valor atual do patrimônio
        valor_aporte_total (float): Valor do aporte adicional
    """
    patrimonio_total = patrimonio_atual + valor_aporte_total
    
    print(f"Patrimônio atual: R$ {patrimonio_atual:,.2f}")
    print(f"Valor de aporte: R$ {valor_aporte_total:,.2f}")
    print(f"Patrimônio total após aporte: R$ {patrimonio_total:,.2f}")
    print("\n" + "="*50)


def exibir_tabela_detalhada(ativos_atuais, percentuais_atuais, percentuais_alvo, valores_alvo, acoes_necessarias):
    """
    Exibe tabela detalhada com informações de cada ativo.
    
    Args:
        ativos_atuais (dict): Valores atuais dos ativos
        percentuais_atuais (dict): Percentuais atuais dos ativos
        percentuais_alvo (dict): Percentuais alvo dos ativos
        valores_alvo (dict): Valores alvo dos ativos
        acoes_necessarias (dict): Ações necessárias para cada ativo
    """
    print(f"{'Ativo':<10} {'Atual':<12} {'%Atual':<8} {'%Alvo':<8} {'Valor Alvo':<12} {'Ação':<12}")
    print("-" * 70)
    
    for ativo in ativos_atuais.keys():
        valor_atual = ativos_atuais[ativo]
        percentual_atual = percentuais_atuais[ativo]
        percentual_alvo = percentuais_alvo[ativo]
        valor_alvo = valores_alvo[ativo]
        diferenca = acoes_necessarias[ativo]
        acao_str = formatar_acao(diferenca)
        
        print(f"{ativo:<10} R$ {valor_atual:<10.2f} {percentual_atual:<7.1f}% {percentual_alvo:<7.1f}% R$ {valor_alvo:<10.2f} {acao_str}")


def exibir_resumo_final(total_aportes, total_vendas, valor_aporte_total):
    """
    Exibe resumo final com totais de aportes e vendas.
    
    Args:
        total_aportes (float): Total de aportes necessários
        total_vendas (float): Total de vendas necessárias
        valor_aporte_total (float): Valor de aporte disponível
    """
    print("-" * 70)
    print(f"Total de aportes necessários: R$ {total_aportes:,.2f}")
    print(f"Total de vendas necessárias: R$ {total_vendas:,.2f}")
    print(f"Diferença: R$ {total_aportes - total_vendas:,.2f}")
    
    if abs(total_aportes - total_vendas - valor_aporte_total) > 0.01:
        print(f"\n⚠️  ATENÇÃO: A diferença entre aportes e vendas ({total_aportes - total_vendas:.2f}) não confere com o valor de aporte disponível ({valor_aporte_total:.2f})")


def calcular_rebalanceamento(ativos_atuais, percentuais_alvo, valor_aporte_total=0):
    """
    Calcula os aportes ou vendas necessários para atingir os percentuais alvo de cada ativo.
    
    Args:
        ativos_atuais (dict): Dicionário com nome do ativo como chave e valor atual como valor
                             Exemplo: {'ITSA4': 1000, 'PETR4': 1500, 'VALE3': 800}
        percentuais_alvo (dict): Dicionário com nome do ativo como chave e percentual alvo (0-100) como valor
                                Exemplo: {'ITSA4': 30, 'PETR4': 40, 'VALE3': 30}
        valor_aporte_total (float): Valor total disponível para aporte (padrão: 0)
    
    Returns:
        dict: Dicionário com as ações necessárias para cada ativo
              Valores positivos = aporte necessário
              Valores negativos = venda necessária
    """
    # Validar entradas
    validar_entradas(ativos_atuais, percentuais_alvo)
    
    # Calcular valores básicos
    patrimonio_atual = sum(ativos_atuais.values())
    patrimonio_total = patrimonio_atual + valor_aporte_total
    
    # Exibir resumo do patrimônio
    exibir_resumo_patrimonio(patrimonio_atual, valor_aporte_total)
    
    # Calcular percentuais e valores
    percentuais_atuais = calcular_percentuais_atuais(ativos_atuais)
    valores_alvo = calcular_valores_alvo(percentuais_alvo, patrimonio_total)
    
    # Calcular ações necessárias
    acoes_necessarias, total_aportes, total_vendas = calcular_acoes_necessarias(ativos_atuais, valores_alvo)
    
    # Exibir resultados
    exibir_tabela_detalhada(ativos_atuais, percentuais_atuais, percentuais_alvo, valores_alvo, acoes_necessarias)
    exibir_resumo_final(total_aportes, total_vendas, valor_aporte_total)
    
    return acoes_necessarias


def calcular_rebalanceamento_com_fixos(ativos_atuais, percentuais_alvo, valor_aporte_total=0, ativos_fixos=None):
    """
    Calcula os aportes ou vendas necessários considerando ativos que devem ser mantidos fixos.
    
    Args:
        ativos_atuais (dict): Dicionário com nome do ativo como chave e valor atual como valor
        percentuais_alvo (dict): Dicionário com nome do ativo como chave e percentual alvo (0-100) como valor
        valor_aporte_total (float): Valor total disponível para aporte (padrão: 0)
        ativos_fixos (list): Lista de ativos que devem ser mantidos fixos (opcional)
    
    Returns:
        dict: Dicionário com as ações necessárias para cada ativo
              Valores positivos = aporte necessário
              Valores negativos = venda necessária
              Valores zero = ativo mantido fixo
    """
    # Validar entradas
    validar_entradas(ativos_atuais, percentuais_alvo)
    
    # Se não há ativos fixos, usar função padrão
    if not ativos_fixos:
        return calcular_rebalanceamento(ativos_atuais, percentuais_alvo, valor_aporte_total)
    
    # Validar ativos fixos
    is_valid, error_msg, _ = validar_ativos_fixos(ativos_atuais, ativos_fixos, percentuais_alvo)
    if not is_valid:
        raise ValueError(error_msg)
    
    # Calcular valores básicos
    patrimonio_atual = sum(ativos_atuais.values())
    patrimonio_total = patrimonio_atual + valor_aporte_total
    
    # Exibir resumo do patrimônio
    exibir_resumo_patrimonio(patrimonio_atual, valor_aporte_total)
    print(f"Ativos fixos (não serão alterados): {', '.join(ativos_fixos)}")
    print("="*50)
    
    # Calcular percentuais e valores considerando ativos fixos
    percentuais_atuais = calcular_percentuais_atuais(ativos_atuais)
    valores_alvo = calcular_valores_alvo_com_fixos(ativos_atuais, percentuais_alvo, patrimonio_total, ativos_fixos)
    
    # Calcular ações necessárias
    acoes_necessarias, total_aportes, total_vendas = calcular_acoes_necessarias(ativos_atuais, valores_alvo)
    
    # Zerar ações para ativos fixos
    for ativo in ativos_fixos:
        acoes_necessarias[ativo] = 0.0
    
    # Recalcular totais excluindo ativos fixos
    total_aportes = sum(valor for ativo, valor in acoes_necessarias.items() 
                       if valor > 0 and ativo not in ativos_fixos)
    total_vendas = sum(abs(valor) for ativo, valor in acoes_necessarias.items() 
                      if valor < 0 and ativo not in ativos_fixos)
    
    # Exibir resultados
    exibir_tabela_detalhada_com_fixos(ativos_atuais, percentuais_atuais, percentuais_alvo, 
                                     valores_alvo, acoes_necessarias, ativos_fixos)
    exibir_resumo_final(total_aportes, total_vendas, valor_aporte_total)
    
    return acoes_necessarias


def exibir_tabela_detalhada_com_fixos(ativos_atuais, percentuais_atuais, percentuais_alvo, valores_alvo, acoes_necessarias, ativos_fixos):
    """
    Exibe tabela detalhada com informações de cada ativo, destacando os fixos.
    """
    print(f"{'Ativo':<10} {'Atual':<12} {'%Atual':<8} {'%Alvo':<8} {'Valor Alvo':<12} {'Ação':<12} {'Status':<8}")
    print("-" * 80)
    
    for ativo in ativos_atuais.keys():
        valor_atual = ativos_atuais[ativo]
        percentual_atual = percentuais_atuais[ativo]
        percentual_alvo = percentuais_alvo[ativo]
        valor_alvo = valores_alvo[ativo]
        diferenca = acoes_necessarias[ativo]
        
        if ativo in ativos_fixos:
            acao_str = "FIXO"
            status = "🔒"
        else:
            acao_str = formatar_acao(diferenca)
            status = "📈" if diferenca > 0 else "📉" if diferenca < 0 else "✅"
        
        print(f"{ativo:<10} R$ {valor_atual:<10.2f} {percentual_atual:<7.1f}% {percentual_alvo:<7.1f}% R$ {valor_alvo:<10.2f} {acao_str:<12} {status}")


def calcular_aporte_necessario_para_alvo(ativos_atuais, percentuais_alvo, ativos_fixos=None):
    """
    Calcula o aporte mínimo necessário para atingir os percentuais alvo sem vender nenhum ativo.
    Considera um cenário de "aporte infinito" onde só se compra, nunca se vende.
    
    Args:
        ativos_atuais (dict): Valores atuais dos ativos
        percentuais_alvo (dict): Percentuais alvo de cada ativo (0-100)
        ativos_fixos (list): Lista de ativos que devem ser mantidos fixos (opcional)
    
    Returns:
        dict: {
            'aporte_total_necessario': float,
            'patrimonio_final': float,
            'aportes_por_ativo': dict,
            'valores_finais': dict,
            'percentuais_finais': dict
        }
    """
    # Validar entradas
    validar_entradas(ativos_atuais, percentuais_alvo)
    
    patrimonio_atual = sum(ativos_atuais.values())
    
    if ativos_fixos:
        # Validar ativos fixos
        is_valid, error_msg, _ = validar_ativos_fixos(ativos_atuais, ativos_fixos, percentuais_alvo)
        if not is_valid:
            raise ValueError(error_msg)
    
    print(f"CÁLCULO DE APORTE NECESSÁRIO PARA ATINGIR ALVOS")
    print("=" * 55)
    print(f"Patrimônio atual: R$ {patrimonio_atual:,.2f}")
    if ativos_fixos:
        print(f"Ativos fixos: {', '.join(ativos_fixos)}")
    print("Estratégia: Apenas aportes (sem vendas)")
    print()
    
    # Identificar ativos que precisam de aporte
    percentuais_atuais = calcular_percentuais_atuais(ativos_atuais)
    ativos_precisam_aporte = []
    
    for ativo, perc_atual in percentuais_atuais.items():
        perc_alvo = percentuais_alvo[ativo]
        if perc_atual < perc_alvo:  # Ativo está abaixo do alvo
            ativos_precisam_aporte.append(ativo)
    
    # Se há ativos fixos, remove eles da lista de aportes
    if ativos_fixos:
        ativos_precisam_aporte = [a for a in ativos_precisam_aporte if a not in ativos_fixos]
    
    if not ativos_precisam_aporte:
        print("✅ Nenhum aporte necessário! Todos os ativos já estão no alvo ou acima.")
        return {
            'aporte_total_necessario': 0,
            'patrimonio_final': patrimonio_atual,
            'aportes_por_ativo': {ativo: 0 for ativo in ativos_atuais.keys()},
            'valores_finais': ativos_atuais.copy(),
            'percentuais_finais': percentuais_atuais.copy()
        }
    
    # Calcular o patrimônio final necessário
    # Usamos o ativo que está mais "longe" do alvo como referência
    patrimonio_final_necessario = 0
    
    for ativo in ativos_atuais.keys():
        valor_atual = ativos_atuais[ativo]
        perc_alvo = percentuais_alvo[ativo]
        
        # Para ativos fixos, eles definem uma restrição no patrimônio total
        if ativos_fixos and ativo in ativos_fixos:
            patrimonio_minimo_para_este_ativo = valor_atual / (perc_alvo / 100)
            patrimonio_final_necessario = max(patrimonio_final_necessario, patrimonio_minimo_para_este_ativo)
        # Para ativos que não precisam de aporte (já estão acima do alvo)
        elif ativo not in ativos_precisam_aporte:
            patrimonio_minimo_para_este_ativo = valor_atual / (perc_alvo / 100)
            patrimonio_final_necessario = max(patrimonio_final_necessario, patrimonio_minimo_para_este_ativo)
    
    # Se nenhum ativo restringiu o patrimônio, calcular baseado nos que precisam de aporte
    if patrimonio_final_necessario == 0:
        # Usar uma abordagem iterativa para encontrar o patrimônio ideal
        patrimonio_final_necessario = patrimonio_atual * 2  # Chute inicial
        
        for _ in range(100):  # Limite de iterações para evitar loop infinito
            todos_ativos_ok = True
            for ativo, valor_atual in ativos_atuais.items():
                perc_alvo = percentuais_alvo[ativo]
                valor_alvo = (perc_alvo / 100) * patrimonio_final_necessario
                
                if valor_alvo < valor_atual:  # Precisaria vender
                    patrimonio_final_necessario = valor_atual / (perc_alvo / 100)
                    todos_ativos_ok = False
                    break
            
            if todos_ativos_ok:
                break
    
    # Calcular valores finais e aportes
    aporte_total = patrimonio_final_necessario - patrimonio_atual
    valores_finais = {}
    aportes_por_ativo = {}
    
    for ativo, valor_atual in ativos_atuais.items():
        perc_alvo = percentuais_alvo[ativo]
        valor_final = (perc_alvo / 100) * patrimonio_final_necessario
        aporte_ativo = max(0, valor_final - valor_atual)  # Não permite vendas
        
        valores_finais[ativo] = valor_atual + aporte_ativo
        aportes_por_ativo[ativo] = aporte_ativo
    
    # Calcular percentuais finais
    percentuais_finais = {}
    patrimonio_final_real = sum(valores_finais.values())
    for ativo, valor_final in valores_finais.items():
        percentuais_finais[ativo] = (valor_final / patrimonio_final_real) * 100
    
    # Exibir resultados
    exibir_resultado_aporte_infinito(ativos_atuais, percentuais_atuais, percentuais_alvo, 
                                   valores_finais, aportes_por_ativo, percentuais_finais, 
                                   aporte_total, ativos_fixos)
    
    return {
        'aporte_total_necessario': aporte_total,
        'patrimonio_final': patrimonio_final_real,
        'aportes_por_ativo': aportes_por_ativo,
        'valores_finais': valores_finais,
        'percentuais_finais': percentuais_finais
    }


def exibir_resultado_aporte_infinito(ativos_atuais, percentuais_atuais, percentuais_alvo, 
                                   valores_finais, aportes_por_ativo, percentuais_finais, 
                                   aporte_total, ativos_fixos):
    """
    Exibe os resultados do cálculo de aporte infinito de forma organizada.
    """
    print(f"{'Ativo':<15} {'Atual':<12} {'%Atual':<8} {'%Alvo':<8} {'Final':<12} {'%Final':<8} {'Aporte':<12} {'Status':<8}")
    print("-" * 95)
    
    for ativo in ativos_atuais.keys():
        valor_atual = ativos_atuais[ativo]
        percentual_atual = percentuais_atuais[ativo]
        percentual_alvo = percentuais_alvo[ativo]
        valor_final = valores_finais[ativo]
        percentual_final = percentuais_finais[ativo]
        aporte_ativo = aportes_por_ativo[ativo]
        
        if ativos_fixos and ativo in ativos_fixos:
            status = "🔒 FIXO"
        elif aporte_ativo > 0:
            status = "� APORTE"
        else:
            status = "✅ OK"
        
        aporte_str = f"R$ {aporte_ativo:,.2f}" if aporte_ativo > 0 else "-"
        
        print(f"{ativo:<15} R$ {valor_atual:<10.2f} {percentual_atual:<7.1f}% {percentual_alvo:<7.1f}% "
              f"R$ {valor_final:<10.2f} {percentual_final:<7.1f}% {aporte_str:<12} {status}")
    
    print("-" * 95)
    print(f"APORTE TOTAL NECESSÁRIO: R$ {aporte_total:,.2f}")
    print(f"PATRIMÔNIO FINAL: R$ {sum(valores_finais.values()):,.2f}")
    
    # Verificar se todos os alvos foram atingidos
    todos_alvos_ok = True
    for ativo in ativos_atuais.keys():
        diff = abs(percentuais_finais[ativo] - percentuais_alvo[ativo])
        if diff > 0.01:  # Tolerância de 0.01%
            todos_alvos_ok = False
            break
    
    if todos_alvos_ok:
        print("✅ Todos os alvos serão atingidos!")
    else:
        print("⚠️  Alguns alvos podem não ser atingidos perfeitamente devido a restrições.")


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
                'motivo_inviabilidade': f"Ativos fixos incompatíveis: {error_msg}",
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
        print(f"Ativos fixos: {', '.join(ativos_fixos)}")
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
    Calcula o patrimônio alvo mínimo considerando restrições dos ativos fixos
    e ativos que não podem ser vendidos abaixo do valor atual.
    """
    patrimonio_alvo = 0
    
    for ativo, valor_atual in ativos_atuais.items():
        perc_alvo = percentuais_alvo[ativo]
        
        if ativo in ativos_fixos:
            # Ativos fixos definem uma restrição rígida
            patrimonio_minimo = valor_atual / (perc_alvo / 100)
            patrimonio_alvo = max(patrimonio_alvo, patrimonio_minimo)
    
    # Se nenhum ativo fixo definiu o patrimônio, usar o patrimônio atual como base
    if patrimonio_alvo == 0:
        patrimonio_alvo = sum(ativos_atuais.values())
        
        # Verificar se algum ativo não fixo precisa de mais patrimônio
        for ativo, valor_atual in ativos_atuais.items():
            if ativo not in ativos_fixos:
                perc_alvo = percentuais_alvo[ativo]
                perc_atual = (valor_atual / patrimonio_alvo) * 100
                
                # Se o ativo está muito acima do alvo, pode precisar aumentar o patrimônio total
                if perc_atual > perc_alvo:
                    patrimonio_minimo_para_este = valor_atual / (perc_alvo / 100)
                    patrimonio_alvo = max(patrimonio_alvo, patrimonio_minimo_para_este)
    
    return patrimonio_alvo


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
                'motivo_inviabilidade': f"Ativos fixos incompatíveis: {error_msg}",
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
    # Para executar exemplos, rode: python examples.py
    # Para executar a interface, rode: streamlit run app.py
    print("Sistema de Rebalanceamento de Ativos")
    print("="*40)
    print("Funções disponíveis:")
    print("• calcular_rebalanceamento()")
    print("• calcular_rebalanceamento_com_fixos()")
    print("• calcular_aporte_necessario_para_alvo()")
    print("• calcular_rebalanceamento_otimizado()")
    print()
    print("Para ver exemplos de uso, execute:")
    print("python examples.py")
    print()
    print("Para acessar a interface web, execute:")
    print("streamlit run app.py")