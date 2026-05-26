import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math

# Importa o módulo de exportação DXF
from exportar_dxf import exportar_dxf

# Configuração da Interface
st.set_page_config(page_title="Projeto Estaca Raiz - NBR 6122", layout="wide")

# ==========================================
# 1. CONSTANTES E PADRÕES
# ==========================================
DADOS_ESTACA = {
    150: {"rocha": 150, "revest": 127},
    160: {"rocha": 150, "revest": 141},
    200: {"rocha": 160, "revest": 168},
    250: {"rocha": 200, "revest": 220},
    310: {"rocha": 250, "revest": 273},
    400: {"rocha": 310, "revest": 355},
    450: {"rocha": 400, "revest": 406}
}

BITOLAS_ACO = [10.0, 12.5, 16.0, 20.0, 25.0, 32.0]
BITOLAS_ESTRIBO = [5.0, 6.3, 8.0, 10.0]
COBRIMENTOS = list(range(40, 105, 10))  # 40, 50, 60, 70, 80, 90, 100

# ==========================================
# 2. ENTRADAS DO USUÁRIO
# ==========================================
st.sidebar.header("📊 Parâmetros")

d_solo_sel = st.sidebar.selectbox("Ø Nominal Solo (mm)", list(DADOS_ESTACA.keys()), index=6)
cob_solo = st.sidebar.selectbox("Cobrimento Estrutural (mm)", COBRIMENTOS, index=1, help="Descontado a partir do diâmetro do tubo de revestimento. A visualização mostra também o cobrimento relativo ao Ø acabado da estaca e Ø externo do estribo.")

st.sidebar.subheader("🏗️ Armadura")
n_barras = st.sidebar.number_input("Nº de Barras", 4, 30, 10, step=1)
d_barra_sel = st.sidebar.selectbox("Ø Barra (mm)", BITOLAS_ACO, index=3)
d_estribo_sel = st.sidebar.selectbox("Ø Estribo (mm)", BITOLAS_ESTRIBO, index=1)
passo_estribo = st.sidebar.number_input("Passo Estribo (cm)", 5.0, 30.0, 15.0)

st.sidebar.subheader("🏗️ Ancoragem no Bloco de Coroamento")
h_bloco = st.sidebar.number_input("Altura do Bloco (m)", 0.5, 5.0, 1.5, step=0.1)
cob_bloco = st.sidebar.number_input("Cobrimento do Bloco (cm)", 5, 50, 10, step=5)
l_solo = st.sidebar.number_input("Trecho em Solo (m)", 1.0, 50.0, 10.0)
l_rocha = st.sidebar.number_input("Embutimento Rocha (m)", 0.0, 10.0, 3.0)

# ==========================================
# 3. NOVA LÓGICA DE CÁLCULOS (GEO vs EST)
# ==========================================
d_rocha_nom = DADOS_ESTACA[d_solo_sel]["rocha"]

# Seções Efetivas
d_solo_geo = d_solo_sel
d_solo_est = DADOS_ESTACA[d_solo_sel]["revest"]
d_rocha_geo_est = DADOS_ESTACA[d_rocha_nom]["revest"] # Rocha assume o revestimento da nominal reduzida

# Raios para desenho e cálculo
r_s_geo = d_solo_geo / 2
r_s_est = d_solo_est / 2
r_r_geo_est = d_rocha_geo_est / 2

# A gaiola agora é calculada COM BASE NA SEÇÃO ESTRUTURAL DO SOLO (Revestimento)
raio_ext_gaiola = r_s_est - cob_solo
raio_eixo_estribo = raio_ext_gaiola - (d_estribo_sel/2)
raio_centro_barra = raio_ext_gaiola - d_estribo_sel - (d_barra_sel/2)
raio_ext_estribo = raio_eixo_estribo + (d_estribo_sel/2)

# Cálculos adicionais de cobrimento para visualização
cobrimento_acabado_solo = r_s_geo - raio_ext_estribo
cobrimento_acabado_rocha = r_r_geo_est - raio_ext_estribo
d_ext_estribo = 2 * raio_ext_estribo

# Cobrimento final na rocha é a diferença entre a nova seção da rocha e a gaiola constante
cobrimento_rocha = r_r_geo_est - raio_ext_gaiola

# ==========================================
# 4. MOTOR DE EXPORTAÇÃO DXF (SEÇÕES + PERFIL)
# ==========================================
# O bloco de exportação é movido para depois da definição de l_espera

# ==========================================
# 5. INTERFACE PRINCIPAL
# ==========================================
st.title("Dimensionamento Geométrico de Estaca Raiz")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ø Geo. Solo (Perfuração)", f"{d_solo_geo} mm")
col2.metric("Ø Est. Solo (Revestimento)", f"{d_solo_est} mm")
col3.metric("Ø Nominal Rocha (Ref.)", f"{d_rocha_nom} mm")
col4.metric("Ø Geo/Est Rocha", f"{d_rocha_geo_est} mm")

st.markdown("---")

c1, c2, c3 = st.columns([1, 1, 1])
area_aco = n_barras * (np.pi*(d_barra_sel/10)**2)/4
c1.metric("Área de Aço Longitudinal", f"{area_aco:.2f} cm²")

# Área de aço na seção do solo (mesma da gaiola)
area_aco_solo = area_aco
area_concreto_solo = np.pi * (d_solo_geo/10)**2 / 4
taxa_aco_solo = (area_aco_solo / area_concreto_solo) * 100
c2.metric("Taxa Aço - Seção Solo", f"{taxa_aco_solo:.2f}%")

# Área de aço na seção da rocha (mesma gaiola, apenas cobrimento muda)
area_aco_rocha = area_aco
area_concreto_rocha = np.pi * (d_rocha_geo_est/10)**2 / 4
taxa_aco_rocha = (area_aco_rocha / area_concreto_rocha) * 100
c3.metric("Taxa Aço - Seção Rocha", f"{taxa_aco_rocha:.2f}%")

# Limites normativos (NBR 6122)
TAXA_MIN = 0.4  # % mínima

# Taxa máxima conforme diâmetro da estaca
if d_solo_sel <= 310:
    TAXA_MAX = 8.0  # % máxima para Ø ≤ 310mm
else:
    TAXA_MAX = 6.0  # % máxima para Ø ≥ 400mm

# Espaçamento mínimo entre barras (NBR 6122)
espacamento_min = max(d_barra_sel, 20)  # 1Ø da barra ou 20mm (o que for maior)

st.markdown("---")
st.subheader("📐 Verificação Normativa (NBR 6122)")

v1, v2, v3, v4 = st.columns(4)
v1.metric("Taxa Mínima", f"≥ {TAXA_MIN}%")
v2.metric(f"Taxa Máxima (Ø{d_solo_sel}mm)", f"≤ {TAXA_MAX}%")

# Verificação Solo
if taxa_aco_solo < TAXA_MIN:
    v3.error(f"⚠️ Solo: {taxa_aco_solo:.2f}% - ABAIXO do mínimo!")
elif taxa_aco_solo > TAXA_MAX:
    v3.error(f"⚠️ Solo: {taxa_aco_solo:.2f}% - ACIMA do máximo!")
else:
    v3.success(f"✅ Solo: {taxa_aco_solo:.2f}% - OK!")

# Verificação Rocha
if taxa_aco_rocha < TAXA_MIN:
    v4.error(f"⚠️ Rocha: {taxa_aco_rocha:.2f}% - ABAIXO do mínimo!")
elif taxa_aco_rocha > TAXA_MAX:
    v4.error(f"⚠️ Rocha: {taxa_aco_rocha:.2f}% - ACIMA do máximo!")
else:
    v4.success(f"✅ Rocha: {taxa_aco_rocha:.2f}% - OK!")

# Verificação de espaçamento entre barras
st.markdown("---")
st.subheader("📏 Espaçamento entre Barras (NBR 6122)")

# Calcula o espaçamento real entre barras (face a face = eixo a eixo - diâmetro da barra)
angulo_step = 2 * np.pi / n_barras
espacamento_eixo = 2 * raio_centro_barra * np.sin(angulo_step / 2)
espacamento_real = espacamento_eixo - d_barra_sel

e1, e2 = st.columns(2)
e1.metric("Espaçamento Mínimo Requiredo", f"≥ {espacamento_min:.1f} mm")

if espacamento_real < espacamento_min:
    e2.error(f"⚠️ Real: {espacamento_real:.1f} mm - ABAIXO do mínimo!")
else:
    e2.success(f"✅ Real: {espacamento_real:.1f} mm - OK!")

# Dimensionamento conforme taxa de aço
st.markdown("---")
st.subheader("🔧 Dimensionamento (NBR 6122)")

if taxa_aco_solo >= 6.0:
    st.warning(f"⚠️ Taxa ≥ 6%: Todo esforço deve ser resistido APENAS pelo aço (concreto desprezado)")
else:
    st.info(f"ℹ️ Taxa < 6%: Estaca trabalha como pilar de concreto (concreto + aço)")

if cobrimento_rocha < 0:
    c2.error(f"⚠️ COLISÃO NA ROCHA: A gaiola é {abs(cobrimento_rocha)*2:.1f} mm MAIOR que o furo na rocha!")
else:
    c2.success(f"✅ OK: Cobrimento na Rocha = {cobrimento_rocha:.1f} mm")

# ==========================================
# CÁLCULOS DE QUANTITATIVOS (ORÇAMENTO)
# ==========================================

# Parâmetros práticos adotados para estaca raiz
l_espera = h_bloco - (cob_bloco / 100) - 0.10  # Arranque dinâmico baseado no bloco
cobrimento_fundo_m = 0.05 # Afastamento do fundo do furo (m)

# 1. Volume de Perfuração (Escavação Teórica em m³)
# Solo: usa diâmetro do revestimento (tubo que desce cortando o terreno)
# Rocha: usa diâmetro do revestimento da nominal reduzida
v_escavacao_solo = (math.pi * (d_solo_est / 1000)**2 / 4) * l_solo
v_escavacao_rocha = (math.pi * (d_rocha_geo_est / 1000)**2 / 4) * l_rocha
v_total_escavacao = v_escavacao_solo + v_escavacao_rocha

# 2. Volume de Argamassa (Geométrico em m³)
v_total_argamassa = v_total_escavacao
peso_cimento = v_total_argamassa * 600 # Estimativa de 600 kg de cimento por m³ de argamassa

# 3. Peso do Aço Longitudinal (kg)
comprimento_barra = l_solo + l_rocha - cobrimento_fundo_m + l_espera
massa_linear_long = (d_barra_sel**2) / 162 # Fórmula prática para peso linear do aço (kg/m)

# Cálculo de trespasses se comprimento > 12m
l_teorico_barra = comprimento_barra
if l_teorico_barra > 12.0:
    trespasse_m = 50 * (d_barra_sel / 1000)  # Trespasse de 50Ø em metros
    num_segmentos = math.ceil(l_teorico_barra / 12.0)
    num_trespasses = num_segmentos - 1
    acrescimo_trespasse = num_trespasses * trespasse_m
    comprimento_barra_total = l_teorico_barra + acrescimo_trespasse
else:
    comprimento_barra_total = l_teorico_barra
    num_trespasses = 0

peso_longitudinal = n_barras * comprimento_barra_total * massa_linear_long

# 4. Peso do Aço Transversal (Estribo Espiral em kg)
d_eixo_estribo_m = (raio_eixo_estribo * 2) / 1000 # Diâmetro da espiral em metros
passo_m = passo_estribo / 100 # Passo em metros

# ==========================================
# 4. MOTOR DE EXPORTAÇÃO DXF (SEÇÕES + PERFIL)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Exportação CAD (AutoCAD)")
nome_arquivo = st.sidebar.text_input("Nome do arquivo (sem .dxf)", f"Secoes_Estaca_{d_solo_sel}mm")

try:
    # Gera o DXF em memória (bytes)
    dxf_bytes = exportar_dxf(
        r_s_geo=r_s_geo,
        r_s_est=r_s_est,
        r_r_geo_est=r_r_geo_est,
        raio_eixo_estribo=raio_eixo_estribo,
        raio_centro_barra=raio_centro_barra,
        d_barra_sel=d_barra_sel,
        n_barras=n_barras,
        l_solo=l_solo,
        l_rocha=l_rocha,
        passo_estribo=passo_estribo,
        l_espera=l_espera,
        nome_arquivo=nome_arquivo,
        return_bytes=True  # Retorna bytes em vez de salvar em disco
    )
    
    # Botão de download
    st.sidebar.download_button(
        label="📥 Baixar DXF",
        data=dxf_bytes,
        file_name=f"{nome_arquivo}.dxf",
        mime="application/dxf"
    )
    st.sidebar.success("✅ Arquivo pronto para download!")
    
except Exception as e:
    st.sidebar.error(f"Erro ao gerar CAD: {e}")


comp_volta = math.sqrt((math.pi * d_eixo_estribo_m)**2 + passo_m**2) # Pitágoras (hipotenusa)
n_voltas = (l_solo + l_rocha - cobrimento_fundo_m) / passo_m

massa_linear_estribo = (d_estribo_sel**2) / 162 # (kg/m)
peso_estribo = n_voltas * comp_volta * massa_linear_estribo

peso_aco_total = peso_longitudinal + peso_estribo

# --- LINHA 3: QUANTITATIVOS ---
st.markdown("---")
st.subheader("📊 Quantitativos Estimados (Por Estaca)")
q1, q2, q3, q4 = st.columns(4)
q1.metric("Escavação Total", f"{v_total_escavacao:.2f} m³")
q2.metric("Argamassa", f"{v_total_argamassa:.2f} m³", f"~{peso_cimento:.0f} kg de Cimento", delta_color="off")
q3.metric("Aço Longitudinal", f"{peso_longitudinal:.1f} kg")
q4.metric("Aço Transversal (Estribo)", f"{peso_estribo:.1f} kg", f"Total: {peso_aco_total:.1f} kg", delta_color="off")

st.markdown("---")
fig = plt.figure(figsize=(16, 8))

def desenhar_secao(ax, raio_furo, raio_revest, titulo, cor_furo, raio_acabado=None, cobrimento_acabado=None):
    ax.add_patch(patches.Circle((0,0), raio_furo, color=cor_furo, alpha=0.3))
    ax.add_patch(patches.Circle((0,0), raio_revest, fill=False, ls='--', color='black', lw=1.5))
    ax.add_patch(patches.Circle((0,0), raio_eixo_estribo, fill=False, color='red', lw=1.2))
    angulos = np.linspace(0, 2*np.pi, int(n_barras), endpoint=False)
    for a in angulos:
        bx, by = raio_centro_barra * np.cos(a), raio_centro_barra * np.sin(a)
        ax.add_patch(patches.Circle((bx, by), d_barra_sel/2, color='blue', zorder=5))

    if raio_acabado is not None and cobrimento_acabado is not None:
        ax.add_patch(patches.Circle((0,0), raio_ext_estribo, fill=False, ls=':', color='darkred', lw=1.2))
        ax.plot([raio_ext_estribo, raio_acabado], [0, 0], color='darkred', lw=1.0)
        ax.text((raio_ext_estribo + raio_acabado) / 2, 0, f"{cobrimento_acabado:.1f} mm",
                color='darkred', fontsize=10, va='bottom', ha='center')
        texto_x = 0.6 * max(r_s_geo, r_r_geo_est)
        texto_y = 0.55 * max(r_s_geo, r_r_geo_est)
        ax.text(
            texto_x, texto_y,
            f"Ø acabado = {2*raio_acabado:.0f} mm\nØ ext. estribo = {d_ext_estribo:.1f} mm\nCob. p/ Ø acabado = {cobrimento_acabado:.1f} mm",
            fontsize=9, color='black', va='bottom', ha='left',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=4)
        )
    
    ax.set_title(titulo, fontweight='bold', fontsize=14)
    max_radius = max(r_s_geo, r_r_geo_est)
    ax.set_xlim(-max_radius-20, max_radius+20); ax.set_ylim(-max_radius-20, max_radius+20)
    ax.set_aspect('equal')
    ax.axis('off')

ax_solo = plt.subplot(1, 3, 1)
desenhar_secao(ax_solo, r_s_geo, r_s_est, "Seção Transversal - SOLO", "#D2B48C", raio_acabado=r_s_geo, cobrimento_acabado=cobrimento_acabado_solo)

ax_rocha = plt.subplot(1, 3, 2)
# Na rocha, furo e revestimento são os mesmos (d_rocha_geo_est)
desenhar_secao(ax_rocha, r_r_geo_est, r_r_geo_est, "Seção Transversal - ROCHA", "#A9A9A9", raio_acabado=r_r_geo_est, cobrimento_acabado=cobrimento_acabado_rocha)

ax_perfil = plt.subplot(1, 3, 3)
ax_perfil.set_title("Perfil Esquemático (Visualização Web)", fontweight='bold', fontsize=14)
ax_perfil.add_patch(patches.Rectangle((-r_s_geo*2, 0), r_s_geo*4, l_solo, color='#F5F5DC', zorder=0))
ax_perfil.add_patch(patches.Rectangle((-r_s_geo*2, -l_rocha), r_s_geo*4, l_rocha, color='#D3D3D3', zorder=0))

# Fustes baseados nas novas dimensões efetivas (Geo)
ax_perfil.add_patch(patches.Rectangle((-r_s_geo, 0), d_solo_geo, l_solo, color='white', ec='black', alpha=0.6))
ax_perfil.add_patch(patches.Rectangle((-r_r_geo_est, -l_rocha), d_rocha_geo_est, l_rocha, color='white', ec='black', alpha=0.8))

cobrimento_fundo_m = 0.15
inicio_gaiola_y = -l_rocha + cobrimento_fundo_m
passo_m = passo_estribo / 100

# Desenha o estribo em perfil como no DXF: um traço zigzag conectando as extremidades
pts_esp = []
half_step = passo_m / 2
y_ptr = inicio_gaiola_y
pts_esp.append((-raio_eixo_estribo, y_ptr))
pts_esp.append((raio_eixo_estribo, y_ptr))

lado_esq = True

y_ptr += half_step
while y_ptr <= l_solo:
    x_pt = -raio_eixo_estribo if lado_esq else raio_eixo_estribo
    pts_esp.append((x_pt, y_ptr))
    lado_esq = not lado_esq
    y_ptr += half_step

# Traço final de retorno
if pts_esp:
    ultimo_x, ultimo_y = pts_esp[-1]
    final_x = raio_eixo_estribo if ultimo_x < 0 else -raio_eixo_estribo
    pts_esp.append((final_x, ultimo_y))
    xs, ys = zip(*pts_esp)
    ax_perfil.plot(xs, ys, color='red', lw=0.8, alpha=0.7)

angulos = np.linspace(0, 2*np.pi, int(n_barras), endpoint=False)
for a in angulos:
    pos_x = raio_centro_barra * np.cos(a)
    ax_perfil.plot([pos_x, pos_x], [inicio_gaiola_y, l_solo], color='blue', lw=2.0)

ax_perfil.axhline(0, color='brown', ls='--', lw=2, label='Nível Rocha')
ax_perfil.set_xlim(-r_s_geo*2.2, r_s_geo*2.2); ax_perfil.set_ylim(-l_rocha-1, l_solo+1)
ax_perfil.set_ylabel("Profundidade (m)")
plt.tight_layout()
st.pyplot(fig)