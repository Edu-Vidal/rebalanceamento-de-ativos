import streamlit as st
import pandas as pd
from script import calcular_rebalanceamento_otimizado_silencioso

# Configuração da página
st.set_page_config(
    page_title="Rebalanceamento de Ativos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Sistema de Rebalanceamento de Ativos")
st.markdown("---")

# Inicializar session state
if 'ativos' not in st.session_state:
    st.session_state.ativos = {}
if 'resultado' not in st.session_state:
    st.session_state.resultado = None

# Sidebar para entrada de dados
st.sidebar.header("💼 Configuração da Carteira")

# Seção para adicionar/remover ativos
st.sidebar.subheader("Adicionar Ativo")
with st.sidebar.form("adicionar_ativo"):
    nome_ativo = st.text_input("Nome do Ativo", placeholder="Ex: ITSA4")
    valor_atual = st.number_input("Valor Atual (R$)", min_value=0.0, step=100.0, format="%.2f")
    percentual_alvo = st.number_input("Percentual Alvo (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.2f")
    
    submitted = st.form_submit_button("Adicionar Ativo")
    
    if submitted and nome_ativo and valor_atual > 0 and percentual_alvo > 0:
        st.session_state.ativos[nome_ativo] = {
            'valor_atual': valor_atual,
            'percentual_alvo': percentual_alvo
        }
        st.sidebar.success(f"Ativo {nome_ativo} adicionado!")

# Exibir ativos atuais e permitir remoção
if st.session_state.ativos:
    st.sidebar.subheader("Ativos na Carteira")
    for ativo in list(st.session_state.ativos.keys()):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.write(f"**{ativo}**")
            st.write(f"R$ {st.session_state.ativos[ativo]['valor_atual']:,.2f} ({st.session_state.ativos[ativo]['percentual_alvo']:.1f}%)")
        with col2:
            if st.button("🗑️", key=f"remove_{ativo}", help=f"Remover {ativo}"):
                del st.session_state.ativos[ativo]
                st.rerun()

# Área principal
col1, col2 = st.columns([2, 1])

with col1:
    if st.session_state.ativos:
        # Verificar se soma dos percentuais é 100%
        soma_percentuais = sum(ativo['percentual_alvo'] for ativo in st.session_state.ativos.values())
        
        if abs(soma_percentuais - 100) > 0.01:
            st.error(f"⚠️ A soma dos percentuais alvo deve ser 100%. Atual: {soma_percentuais:.2f}%")
        else:
            st.success(f"✅ Soma dos percentuais: {soma_percentuais:.2f}%")
        
        # Tabela com ativos atuais
        st.subheader("📋 Carteira Atual")
        df_ativos = pd.DataFrame.from_dict(st.session_state.ativos, orient='index')
        df_ativos.columns = ['Valor Atual (R$)', 'Percentual Alvo (%)']
        df_ativos['Valor Atual (R$)'] = df_ativos['Valor Atual (R$)'].apply(lambda x: f"R$ {x:,.2f}")
        df_ativos['Percentual Alvo (%)'] = df_ativos['Percentual Alvo (%)'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_ativos, use_container_width=True)
        
        # Patrimônio total
        patrimonio_total = sum(ativo['valor_atual'] for ativo in st.session_state.ativos.values())
        st.metric("💰 Patrimônio Total", f"R$ {patrimonio_total:,.2f}")
        
    else:
        st.info("👈 Adicione ativos na barra lateral para começar")

with col2:
    if st.session_state.ativos and abs(soma_percentuais - 100) <= 0.01:
        st.subheader("⚙️ Configurações do Cálculo")
        
        # Seleção de ativos fixos
        ativos_disponiveis = list(st.session_state.ativos.keys())
        ativos_fixos = st.multiselect(
            "🔒 Ativos Fixos (não serão alterados)",
            ativos_disponiveis,
            help="Selecione os ativos que devem manter seu valor atual"
        )
        
        # Botão para calcular
        if st.button("🚀 Calcular Rebalanceamento", type="primary", use_container_width=True):
            # Preparar dados para o cálculo
            ativos_atuais = {ativo: dados['valor_atual'] for ativo, dados in st.session_state.ativos.items()}
            percentuais_alvo = {ativo: dados['percentual_alvo'] for ativo, dados in st.session_state.ativos.items()}
            
            # Realizar cálculo
            with st.spinner("Calculando..."):
                resultado = calcular_rebalanceamento_otimizado_silencioso(
                    ativos_atuais=ativos_atuais,
                    percentuais_alvo=percentuais_alvo,
                    ativos_fixos=ativos_fixos if ativos_fixos else None
                )
                st.session_state.resultado = resultado
            
            st.success("✅ Cálculo realizado!")

# Exibir resultados
if st.session_state.resultado:
    resultado = st.session_state.resultado
    
    st.markdown("---")
    st.header("📊 Resultados do Rebalanceamento")
    
    if not resultado['viavel']:
        st.error(f"❌ **Rebalanceamento não é viável:** {resultado['motivo_inviabilidade']}")
    else:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Patrimônio Atual",
                f"R$ {resultado['patrimonio_atual']:,.2f}"
            )
        
        with col2:
            st.metric(
                "🎯 Patrimônio Alvo",
                f"R$ {resultado['patrimonio_alvo']:,.2f}",
                delta=f"R$ {resultado['patrimonio_alvo'] - resultado['patrimonio_atual']:,.2f}"
            )
        
        with col3:
            st.metric(
                "📈 Aporte Necessário",
                f"R$ {resultado['aporte_necessario']:,.2f}"
            )
        
        with col4:
            st.metric(
                "💸 Total de Vendas",
                f"R$ {resultado['total_vendas']:,.2f}"
            )
        
        # Tabela detalhada dos resultados
        st.subheader("📋 Detalhamento por Ativo")
        
        # Preparar dados para a tabela
        dados_tabela = []
        for ativo in st.session_state.ativos.keys():
            valor_atual = resultado['patrimonio_atual'] and st.session_state.ativos[ativo]['valor_atual'] or 0
            percentual_atual = resultado['percentuais_atuais'].get(ativo, 0)
            percentual_alvo = st.session_state.ativos[ativo]['percentual_alvo']
            valor_final = resultado['valores_finais'].get(ativo, 0)
            percentual_final = resultado['percentuais_finais'].get(ativo, 0)
            acao = resultado['acoes_por_ativo'].get(ativo, 0)
            
            # Determinar status e ação
            if acao > 0:
                acao_str = f"Comprar R$ {acao:,.2f}"
                status = "📈 Compra"
            elif acao < 0:
                acao_str = f"Vender R$ {abs(acao):,.2f}"
                status = "📉 Venda"
            elif ativo in (ativos_fixos if 'ativos_fixos' in locals() else []):
                acao_str = "Fixo"
                status = "🔒 Fixo"
            else:
                acao_str = "Manter"
                status = "✅ OK"
            
            dados_tabela.append({
                'Ativo': ativo,
                'Valor Atual': f"R$ {valor_atual:,.2f}",
                '% Atual': f"{percentual_atual:.1f}%",
                '% Alvo': f"{percentual_alvo:.1f}%",
                'Valor Final': f"R$ {valor_final:,.2f}",
                '% Final': f"{percentual_final:.1f}%",
                'Ação Necessária': acao_str,
                'Status': status
            })
        
        df_resultado = pd.DataFrame(dados_tabela)
        
        # Aplicar cores condicionais
        def colorir_status(val):
            if "Compra" in val:
                return 'background-color: #e8f5e8'
            elif "Venda" in val:
                return 'background-color: #ffe8e8'
            elif "Fixo" in val:
                return 'background-color: #f0f0f0'
            else:
                return 'background-color: #e8f8ff'
        
        styled_df = df_resultado.style.applymap(colorir_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Resumo das ações
        st.subheader("📝 Resumo das Ações")
        
        compras = [ativo for ativo, acao in resultado['acoes_por_ativo'].items() if acao > 0]
        vendas = [ativo for ativo, acao in resultado['acoes_por_ativo'].items() if acao < 0]
        fixos = ativos_fixos if 'ativos_fixos' in locals() and ativos_fixos else []
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if compras:
                st.success("📈 **Compras Necessárias:**")
                for ativo in compras:
                    valor = resultado['acoes_por_ativo'][ativo]
                    st.write(f"• {ativo}: R$ {valor:,.2f}")
            else:
                st.info("Nenhuma compra necessária")
        
        with col2:
            if vendas:
                st.warning("📉 **Vendas Necessárias:**")
                for ativo in vendas:
                    valor = abs(resultado['acoes_por_ativo'][ativo])
                    st.write(f"• {ativo}: R$ {valor:,.2f}")
            else:
                st.info("Nenhuma venda necessária")
        
        with col3:
            if fixos:
                st.info("🔒 **Ativos Fixos:**")
                for ativo in fixos:
                    valor = st.session_state.ativos[ativo]['valor_atual']
                    st.write(f"• {ativo}: R$ {valor:,.2f}")
            else:
                st.info("Nenhum ativo fixo")
        
        # Verificação de balanço
        if resultado['aporte_necessario'] <= 0:
            st.success("✅ **Rebalanceamento possível apenas com vendas internas!**")
        else:
            st.info(f"💰 **Aporte externo necessário:** R$ {resultado['aporte_necessario']:,.2f}")

# Rodapé
st.markdown("---")
st.markdown(
    "💡 **Dica:** O sistema calcula automaticamente as ações necessárias para atingir seus percentuais alvo "
    "com o menor aporte possível, utilizando vendas internas quando benéfico."
)

def main():
    """Função principal para execução via Poetry script"""
    pass

if __name__ == "__main__":
    main()
