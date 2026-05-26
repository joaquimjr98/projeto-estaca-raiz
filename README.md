# 🏗️ Projeto Estaca Raiz - NBR 6122

Aplicação web para dimensionamento, cálculo e exportação de detalhamento de estacas raiz conforme NBR 6122.

## 📋 Funcionalidades

- Cálculo de parâmetros geométricos e estruturais
- Visualização 2D em tempo real (seção transversal e perfil)
- Exportação em DXF para AutoCAD
- Interface intuitiva e responsiva

## 🚀 Como usar (Local)

### Requisitos
- Python 3.9+
- pip

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/projeto-estaca-raiz.git
cd projeto-estaca-raiz

# Criar ambiente virtual (opcional mas recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Executar

```bash
streamlit run estaca_raiz.py
```

A aplicação abrirá em `http://localhost:8501`

## 🌐 Usar Online (Streamlit Cloud)

Acesse a aplicação em produção: [seu-link-aqui]

## 📁 Estrutura

```
.
├── estaca_raiz.py           # Aplicação principal (Streamlit)
├── exportar_dxf.py          # Módulo de exportação DXF
├── TEMPLATE.dxf             # Template para detalhamento
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```

## 📝 Entrada de Dados

1. **Características da Estaca**: Diâmetro nominal do solo
2. **Armadura**: Número de barras, bitola, estribo e espaçamento
3. **Dimensões**: Comprimento em solo, embutimento na rocha
4. **Bloco de Coroamento**: Altura e cobrimento

## 💾 Saída

- Gráficos 2D interativos (seção e perfil)
- Tabela de resumo dos parâmetros
- Arquivo DXF para detalhamento em AutoCAD

## 👨‍💻 Autor

[Seu Nome]

## 📄 Licença

MIT
