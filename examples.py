from script import (
    calcular_rebalanceamento, 
    calcular_rebalanceamento_com_fixos,
    calcular_aporte_necessario_para_alvo,
    calcular_rebalanceamento_otimizado,
    validar_ativos_fixos
)


def exemplo_uso_basico():
    """Exemplos básicos de uso das funções de rebalanceamento"""
    
    # Exemplo 1: Rebalanceamento sem aporte adicional
    print("EXEMPLO 1: Rebalanceamento sem aporte adicional")
    print("=" * 50)
    
    ativos = {
        'ITSA4': 2000,
        'PETR4': 3000,
        'VALE3': 1000
    }
    
    percentuais_alvo = {
        'ITSA4': 33.33,
        'PETR4': 33.33,
        'VALE3': 33.34
    }
    
    resultado1 = calcular_rebalanceamento(ativos, percentuais_alvo)
    
    print("\n\n")
    
    # Exemplo 2: Rebalanceamento com aporte adicional
    print("EXEMPLO 2: Rebalanceamento com aporte de R$ 1.000")
    print("=" * 50)
    
    resultado2 = calcular_rebalanceamento(ativos, percentuais_alvo, valor_aporte_total=1000)
    
    return resultado1, resultado2


def exemplo_uso_com_fixos():
    """Exemplo de uso da função calcular_rebalanceamento_com_fixos"""
    
    print("EXEMPLO 3: Rebalanceamento mantendo ITSA4 fixo")
    print("=" * 50)
    
    ativos = {
        'ITSA4': 2000,
        'PETR4': 3000,
        'VALE3': 1000,
        'BBDC4': 1500
    }
    
    # Percentuais que respeitam o valor atual do ITSA4
    patrimonio_total = sum(ativos.values())  # 7500
    percentual_itsa4_atual = (ativos['ITSA4'] / patrimonio_total) * 100  # ~26.67%
    
    percentuais_alvo = {
        'ITSA4': percentual_itsa4_atual,  # Manter percentual atual
        'PETR4': 30.0,
        'VALE3': 20.0,
        'BBDC4': 100 - percentual_itsa4_atual - 30.0 - 20.0  # Resto
    }
    
    print(f"Percentuais alvo ajustados:")
    for ativo, perc in percentuais_alvo.items():
        print(f"  {ativo}: {perc:.2f}%")
    print()
    
    try:
        resultado = calcular_rebalanceamento_com_fixos(
            ativos, 
            percentuais_alvo, 
            valor_aporte_total=1000,
            ativos_fixos=['ITSA4']
        )
        return resultado
    except ValueError as e:
        print(f"❌ Erro: {e}")
        return None


def exemplo_uso_combinacao_invalida():
    """Exemplo que demonstra uma combinação inválida de ativos fixos"""
    
    print("\n\nEXEMPLO 4: Tentativa de combinação inválida")
    print("=" * 50)
    
    ativos = {
        'ITSA4': 2000,
        'PETR4': 3000,
        'VALE3': 1000
    }
    
    # Percentuais incompatíveis com manter ITSA4 fixo
    percentuais_alvo = {
        'ITSA4': 50.0,  # ITSA4 tem ~33% mas queremos 50%
        'PETR4': 30.0,
        'VALE3': 20.0
    }
    
    try:
        resultado = calcular_rebalanceamento_com_fixos(
            ativos, 
            percentuais_alvo, 
            valor_aporte_total=0,
            ativos_fixos=['ITSA4']
        )
        return resultado
    except ValueError as e:
        print(f"❌ Erro esperado: {e}")
        return None


def exemplo_aporte_infinito():
    """Exemplos de cálculo de aporte infinito"""
    
    print("EXEMPLO 5: APORTE INFINITO PARA ATINGIR ALVOS")
    print("="*60)
    
    # Exemplo com carteira desbalanceada que precisa de aportes
    carteira_desbalanceada = {
        'Ações Brasil': 1000,    # Atual: 20%, Alvo: 50%
        'Ações Exterior': 500,   # Atual: 10%, Alvo: 30%
        'Renda Fixa': 3000,      # Atual: 60%, Alvo: 15%
        'REITs': 500             # Atual: 10%, Alvo: 5%
    }
    
    alvos_agressivos = {
        'Ações Brasil': 50.0,
        'Ações Exterior': 30.0,
        'Renda Fixa': 15.0,
        'REITs': 5.0
    }
    
    print("Cenário: Carteira conservadora que quer se tornar mais agressiva")
    print("Estratégia: Apenas aportes (sem vender renda fixa)")
    
    resultado_infinito = calcular_aporte_necessario_para_alvo(carteira_desbalanceada, alvos_agressivos)
    
    print("\n\n" + "="*60)
    print("EXEMPLO 6: APORTE INFINITO COM ATIVOS FIXOS")
    print("="*60)
    
    # Mesmo exemplo, mas mantendo REITs fixo
    print("Cenário: Mesma carteira, mas mantendo REITs inalterado")
    
    try:
        resultado_infinito_fixo = calcular_aporte_necessario_para_alvo(
            carteira_desbalanceada, 
            alvos_agressivos, 
            ativos_fixos=['REITs']
        )
    except ValueError as e:
        print(f"❌ Erro: {e}")
        
        # Vamos ajustar os percentuais para serem compatíveis
        print("\nAjustando percentuais para serem compatíveis com REITs fixo...")
        patrimonio_atual = sum(carteira_desbalanceada.values())
        perc_reits_atual = (carteira_desbalanceada['REITs'] / patrimonio_atual) * 100
        
        alvos_ajustados = {
            'Ações Brasil': 50.0,
            'Ações Exterior': 30.0,
            'Renda Fixa': 100 - 50 - 30 - perc_reits_atual,  # Resto
            'REITs': perc_reits_atual  # Manter atual
        }
        
        print(f"Novos alvos:")
        for ativo, perc in alvos_ajustados.items():
            print(f"  {ativo}: {perc:.2f}%")
        
        resultado_infinito_fixo = calcular_aporte_necessario_para_alvo(
            carteira_desbalanceada, 
            alvos_ajustados, 
            ativos_fixos=['REITs']
        )
    
    return resultado_infinito, resultado_infinito_fixo


def exemplo_rebalanceamento_otimizado():
    """Exemplos de rebalanceamento otimizado"""
    
    print("EXEMPLO 7: Rebalanceamento otimizado sem ativos fixos")
    print("=" * 60)
    
    # Carteira desbalanceada
    carteira = {
        'Ações Nacionais': 5000,    # 50% atual, alvo: 30%
        'Ações Internacionais': 1000,  # 10% atual, alvo: 25%  
        'Renda Fixa': 3000,         # 30% atual, alvo: 35%
        'REITs': 1000              # 10% atual, alvo: 10%
    }
    
    alvos = {
        'Ações Nacionais': 30.0,
        'Ações Internacionais': 25.0,
        'Renda Fixa': 35.0,
        'REITs': 10.0
    }
    
    resultado1 = calcular_rebalanceamento_otimizado(carteira, alvos, valor_aporte_disponivel=1000)
    
    print("\n\nEXEMPLO 8: Mesmo caso com REITs fixo")
    print("=" * 60)
    
    resultado2 = calcular_rebalanceamento_otimizado(carteira, alvos, 
                                                   valor_aporte_disponivel=1000, 
                                                   ativos_fixos=['REITs'])
    
    print("\n\nEXEMPLO 9: Caso impossível - aporte insuficiente")
    print("=" * 60)
    
    # Cenário onde precisa de muito aporte
    carteira_problema = {
        'Ações': 1000,     # 20% atual, alvo: 80%
        'Renda Fixa': 4000  # 80% atual, alvo: 20%
    }
    
    alvos_agressivos = {
        'Ações': 80.0,
        'Renda Fixa': 20.0
    }
    
    resultado3 = calcular_rebalanceamento_otimizado(carteira_problema, alvos_agressivos, 
                                                   valor_aporte_disponivel=500)  # Insuficiente
    
    return resultado1, resultado2, resultado3


def exemplo_validacao_ativos_fixos():
    """Exemplo de validação de ativos fixos"""
    
    print("\n\nEXEMPLO 10: Teste de validação de ativos fixos")
    print("="*60)
    
    # Teste adicional - verificar se validação funciona
    ativos_teste = {
        'Ações Nacionais': 1000, 
        'Fundo Imobiliário': 2000, 
        'Criptomoedas': 1500, 
        'Renda Fixa': 500
    }
    percentuais_teste = {
        'Ações Nacionais': 25, 
        'Fundo Imobiliário': 40, 
        'Criptomoedas': 30, 
        'Renda Fixa': 5
    }

    print("\nTestando validação com Ações Nacionais fixo...")
    is_valid, error, perc_disp = validar_ativos_fixos(ativos_teste, ['Ações Nacionais'], percentuais_teste)

    if is_valid:
        print(f"✅ Validação passou! Percentual disponível: {perc_disp:.2f}%")
        resultado_teste = calcular_rebalanceamento_com_fixos(
            ativos_teste, percentuais_teste, 500, ['Ações Nacionais']
        )
        return resultado_teste
    else:
        print(f"❌ Validação falhou: {error}")
        return None


def executar_todos_exemplos():
    """Executa todos os exemplos disponíveis"""
    
    print("DEMONSTRAÇÃO COMPLETA DO SISTEMA DE REBALANCEAMENTO DE ATIVOS")
    print("=" * 70)
    print()
    
    # Exemplos básicos
    resultado1, resultado2 = exemplo_uso_basico()
    
    print("\n\n")
    
    # Exemplo com ativos fixos
    resultado3 = exemplo_uso_com_fixos()
    
    # Exemplo de combinação inválida
    resultado4 = exemplo_uso_combinacao_invalida()
    
    print("\n\n")
    
    # Exemplos de aporte infinito
    resultado5, resultado6 = exemplo_aporte_infinito()
    
    print("\n\n")
    
    # Exemplos de rebalanceamento otimizado
    resultado7, resultado8, resultado9 = exemplo_rebalanceamento_otimizado()
    
    # Exemplo de validação
    resultado10 = exemplo_validacao_ativos_fixos()
    
    print("\n\n" + "="*70)
    print("DEMONSTRAÇÃO CONCLUÍDA!")
    print("="*70)
    print("Funcionalidades demonstradas:")
    print("✅ Rebalanceamento básico com e sem aportes")
    print("✅ Rebalanceamento com ativos fixos")
    print("✅ Validação de combinações inválidas")
    print("✅ Cálculo de aporte infinito")
    print("✅ Rebalanceamento otimizado com vendas")
    print("✅ Tratamento de casos impossíveis")
    
    return {
        'basico_sem_aporte': resultado1,
        'basico_com_aporte': resultado2,
        'com_fixos': resultado3,
        'combinacao_invalida': resultado4,
        'aporte_infinito': resultado5,
        'aporte_infinito_fixos': resultado6,
        'otimizado': resultado7,
        'otimizado_fixos': resultado8,
        'otimizado_impossivel': resultado9,
        'validacao': resultado10
    }


if __name__ == "__main__":
    # executar_todos_exemplos()
    exemplo_rebalanceamento_otimizado()
