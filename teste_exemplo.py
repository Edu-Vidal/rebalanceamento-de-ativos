#!/usr/bin/env python3
"""
Teste do exemplo específico mencionado pelo usuário
"""

from script import calcular_rebalanceamento_otimizado_silencioso

def testar_exemplo_usuario():
    """
    Testa o exemplo específico:
    A: R$ 10 (1%), B: R$ 10 (50%), C: R$ 50 (49%)
    """
    print("=== TESTE DO EXEMPLO DO USUÁRIO ===")
    print()
    
    # Dados de entrada
    ativos_atuais = {
        'A': 10.0,
        'B': 10.0, 
        'C': 50.0
    }
    
    percentuais_alvo = {
        'A': 1.0,
        'B': 50.0,
        'C': 49.0
    }
    
    print("SITUAÇÃO INICIAL:")
    patrimonio_atual = sum(ativos_atuais.values())
    print(f"Patrimônio atual: R$ {patrimonio_atual:,.2f}")
    
    for ativo, valor in ativos_atuais.items():
        perc_atual = (valor / patrimonio_atual) * 100
        perc_alvo = percentuais_alvo[ativo]
        print(f"  {ativo}: R$ {valor:,.2f} ({perc_atual:.1f}% atual → {perc_alvo:.1f}% alvo)")
    
    print("\nRESULTADO ESPERADO:")
    print("  Patrimônio alvo: ~R$ 102,04")
    print("  A: Vender ~R$ 8,98 (ficar com ~R$ 1,02)")
    print("  B: Comprar ~R$ 41,02 (ficar com ~R$ 51,02)")
    print("  C: Manter R$ 50,00")
    
    # Executar cálculo
    resultado = calcular_rebalanceamento_otimizado_silencioso(ativos_atuais, percentuais_alvo)
    
    print("\nRESULTADO OBTIDO:")
    if resultado['viavel']:
        print(f"  Patrimônio alvo: R$ {resultado['patrimonio_alvo']:,.2f}")
        print(f"  Aporte externo necessário: R$ {resultado['aporte_necessario']:,.2f}")
        print()
        
        for ativo, acao in resultado['acoes_por_ativo'].items():
            valor_atual = ativos_atuais[ativo]
            valor_final = resultado['valores_finais'][ativo]
            
            if acao > 0:
                print(f"  {ativo}: Comprar R$ {acao:,.2f} (de R$ {valor_atual:,.2f} para R$ {valor_final:,.2f})")
            elif acao < 0:
                print(f"  {ativo}: Vender R$ {abs(acao):,.2f} (de R$ {valor_atual:,.2f} para R$ {valor_final:,.2f})")
            else:
                print(f"  {ativo}: Manter R$ {valor_atual:,.2f}")
        
        print(f"\n  Total vendas internas: R$ {resultado['total_vendas']:,.2f}")
        print(f"  Total compras internas: R$ {resultado['total_aportes_internos']:,.2f}")
        
        # Verificar percentuais finais
        print("\n  PERCENTUAIS FINAIS:")
        for ativo, perc_final in resultado['percentuais_finais'].items():
            perc_alvo = percentuais_alvo[ativo]
            print(f"    {ativo}: {perc_final:.2f}% (alvo: {perc_alvo:.1f}%)")
            
    else:
        print(f"  INVIÁVEL: {resultado['motivo_inviabilidade']}")


def testar_casos_adicionais():
    """
    Testa outros casos para validar a lógica
    """
    print("\n\n=== TESTES ADICIONAIS ===")
    
    # Caso 1: Patrimônio atual já é suficiente
    print("\nCASO 1: Patrimônio atual suficiente")
    ativos1 = {'A': 30, 'B': 70}
    alvos1 = {'A': 30, 'B': 70}
    resultado1 = calcular_rebalanceamento_otimizado_silencioso(ativos1, alvos1)
    print(f"Patrimônio alvo: R$ {resultado1['patrimonio_alvo']:,.2f} (atual: R$ 100)")
    
    # Caso 2: Um ativo muito sobrevalorizado
    print("\nCASO 2: Ativo muito sobrevalorizado")
    ativos2 = {'A': 90, 'B': 10}
    alvos2 = {'A': 20, 'B': 80}
    resultado2 = calcular_rebalanceamento_otimizado_silencioso(ativos2, alvos2)
    print(f"Patrimônio alvo: R$ {resultado2['patrimonio_alvo']:,.2f} (atual: R$ 100)")
    if resultado2['viavel']:
        print(f"A: {resultado2['acoes_por_ativo']['A']:+.2f}, B: {resultado2['acoes_por_ativo']['B']:+.2f}")


if __name__ == "__main__":
    testar_exemplo_usuario()
    testar_casos_adicionais()
