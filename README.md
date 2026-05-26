# 🏗️ Projeto Estaca Raiz - NBR 6122

Aplicação web interativa para dimensionamento, cálculo e exportação de detalhamento de estacas raiz conforme NBR 6122.

## 📋 Funcionalidades

- ✨ Cálculo automático de parâmetros geométricos e estruturais
- 📊 Visualização 2D em tempo real (seção transversal em solo/rocha + perfil esquemático)
- 📥 **Download direto de DXF** para AutoCAD (sem salvar em disco)
- ✅ Verificação normativa NBR 6122 (taxa de aço, espaçamento de barras)
- 📈 Quantitativos estimados (escavação, argamassa, aço)
- 🎨 Interface intuitiva com Streamlit

## 🌐 Usar Online (Recomendado)

Acesse a aplicação hospedada no Streamlit Cloud: **[Seu link aqui - será criado após deploy]**

Nenhuma instalação necessária! Basta abrir e usar.

## 🚀 Como usar Localmente

### Requisitos
- Python 3.9 ou superior
- pip (gerenciador de pacotes)

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/joaquimjr98/projeto-estaca-raiz.git
cd projeto-estaca-raiz

# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Executar Localmente

```bash
streamlit run estaca_raiz.py
```

A aplicação abrirá em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
projeto-estaca-raiz/
├── estaca_raiz.py           # Aplicação principal (Streamlit)
├── exportar_dxf.py          # Módulo de exportação para AutoCAD
├── TEMPLATE.dxf             # Template de detalhamento (estilos e layers)
├── requirements.txt         # Dependências Python
├── README.md               # Este arquivo
└── .gitignore
```

## 📝 Como Usar a Aplicação

### 1. **Entrada de Dados (Sidebar)**
   - **Características da Estaca**: Diâmetro nominal do solo
   - **Armadura**: Número de barras, bitola, estribo e espaçamento
   - **Dimensões**: Comprimento em solo, embutimento na rocha
   - **Bloco de Coroamento**: Altura e cobrimento

### 2. **Visualização (Centro da Tela)**
   - Métricas resumidas de dimensões
   - Verificação normativa com status ✅/⚠️
   - Gráficos das seções transversais e perfil

### 3. **Download do DXF (Sidebar)**
   - Digite o nome do arquivo
   - Clique em **"Baixar DXF"**
   - O arquivo é gerado e baixado automaticamente no seu computador

## 💾 Saída

- **Gráficos 2D**: Seção em solo, seção em rocha, perfil esquemático
- **Tabela de parâmetros**: Dimensões, armadura, quantitativos
- **Arquivo DXF**: Detalhamento técnico para AutoCAD (seções + perfil + dimensionamento)

## 🔧 Tecnologias

- **Streamlit**: Interface web interativa
- **ezdxf**: Geração de arquivos DXF (AutoCAD)
- **Matplotlib**: Gráficos 2D
- **NumPy**: Cálculos numéricos

## 📚 Normas Aplicadas

- **NBR 6122** - Projeto e execução de fundações

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! Sinta-se livre para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## 📄 Licença

Este projeto está disponível sob a licença MIT.

## 👨‍💻 Autor

Joaquim Júnior  
Email: joaquimjr98@gmail.com  
GitHub: [@joaquimjr98](https://github.com/joaquimjr98)

---

**Dúvidas?** Abra uma issue no repositório! 🚀
