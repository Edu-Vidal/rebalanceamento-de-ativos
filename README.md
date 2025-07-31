# 📊 Sistema de Rebalanceamento de Ativos

Uma aplicação Streamlit para otimização e rebalanceamento de carteiras de investimento.

## ✨ Funcionalidades

- **Rebalanceamento de Carteira**: Calcule como redistribuir seus ativos para atingir a alocação ideal
- **Otimização de Aportes**: Determine quanto aportar em cada ativo para manter o equilíbrio da carteira
- **Interface Intuitiva**: Interface web amigável com entrada de dados simplificada
- **Análise Visual**: Visualização clara dos resultados e recomendações

## 🚀 Como Executar

### Pré-requisitos

- Python 3.11+
- Poetry (gerenciador de dependências)

### Instalação

1. Clone o repositório:

```bash
git clone <seu-repositorio>
cd "aporte de ativos"
```

2. Instale as dependências:

```bash
poetry install
```

3. Execute a aplicação:

```bash
poetry run streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

### Deploy

Para deploy em produção, utilize os comandos:

```bash
# Instalar dependências
poetry install --only=main

# Executar aplicação
poetry run streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

## 📋 Como Usar

1. **Adicionar Ativos**: Use a sidebar para adicionar os ativos da sua carteira

   - Nome do ativo (ex: ITSA4, PETR4)
   - Valor atual em reais
   - Percentual alvo desejado

2. **Configurar Aporte**: Defina o valor que deseja aportar

3. **Calcular**: O sistema calculará automaticamente:
   - Distribuição atual vs. ideal
   - Quanto aportar em cada ativo
   - Rebalanceamento necessário

## 🛠 Tecnologias

- **Streamlit**: Framework para aplicações web em Python
- **Pandas**: Manipulação e análise de dados
- **Python**: Linguagem de programação

## 📁 Estrutura do Projeto

```
aporte de ativos/
├── app.py              # Aplicação principal Streamlit
├── script.py           # Lógica de cálculo de rebalanceamento
├── examples.py         # Exemplos de uso das funções
├── pyproject.toml      # Configuração do Poetry
└── README.md           # Este arquivo
```

## 🔧 Desenvolvimento

Para contribuir com o projeto:

1. Instale as dependências de desenvolvimento:

```bash
poetry install
```

2. Execute os testes:

```bash
poetry run pytest
```

3. Formate o código:

```bash
poetry run black .
poetry run flake8 .
```

## 📝 Licença

Este projeto está sob a licença MIT.
