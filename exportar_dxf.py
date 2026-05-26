"""
Módulo de Exportação DXF para Estaca Raiz
Gera ficheiro AutoCAD com secções transversais e perfil longitudinal
"""

import ezdxf
import os
import math
import io

def exportar_dxf(
    # Parâmetros geométricos
    r_s_geo,           # Raio geométrico do solo (mm)
    r_s_est,           # Raio estrutural do solo/revestimento (mm)
    r_r_geo_est,       # Raio geométrico/estrutural da rocha (mm)
    raio_eixo_estribo, # Raio do eixo do estribo (mm)
    raio_centro_barra, # Raio do centro das barras (mm)
    d_barra_sel,       # Diâmetro da barra (mm)
    n_barras,          # Número de barras
    
    # Parâmetros do perfil
    l_solo,            # Comprimento em solo (m)
    l_rocha,           # Embutimento na rocha (m)
    passo_estribo,     # Passo do estribo (cm)
    l_espera,          # Comprimento de espera/arranque (m)
    
    # Ficheiro
    nome_arquivo,
    caminho_pasta=None,
    return_bytes=False # Se True, retorna bytes em vez de salvar em disco
):
    """
    Exporta o detalhamento da estaca raiz para DXF utilizando um TEMPLATE.
    As hachuras são desenhadas primeiro para ficarem no fundo (Draw Order).
    """
    
    # ==========================================
    # 1. PREPARAÇÃO DO DOCUMENTO (TEMPLATE)
    # ==========================================
    try:
        # Carrega o template com os estilos: TICK-1_10, 140CL-1_10, 80CL-1_10
        doc = ezdxf.readfile("TEMPLATE.dxf")
    except IOError:
        # Fallback caso o ficheiro não exista
        doc = ezdxf.new(dxfversion='R2000')
        doc.dimstyles.new("TICK-1_10")
        
    # Garantir que o estilo TICK-1_10 existe e está ativo
    if "TICK-1_10" not in doc.dimstyles:
        doc.dimstyles.new("TICK-1_10")
    doc.header['$DIMSTYLE'] = 'TICK-1_10'
        
    msp = doc.modelspace()
    
    # Mapeamento e criação de layers (caso não existam no template)
    camadas = {
        "FORMA_02": 2,      # Contorno (Amarelo)
        "FERRO_05": 5,      # Armadura Longitudinal (Azul)
        "CIVIL-254": 254,   # Hachura Concreto (Cinza)
        "REVESTIMENTO": 1,  # Tubo (Vermelho)
        "ARMADURA": 4,      # Espiral/Estribo (Ciano)
        "PERFIL": 3,        # Contorno Perfil (Verde)
        "CIVIL-TX5": 5,     # Títulos (Azul)
        "CIVIL-TX2": 2      # Escalas (Amarelo)
    }
    
    for nome, cor in camadas.items():
        if nome not in doc.layers:
            doc.layers.add(nome, color=cor)
    
    # Conversão de valores para float estável
    rs_f = round(float(r_s_geo), 4)
    rr_f = round(float(r_r_geo_est), 4)
    rrev_s_f = round(float(r_s_est), 4)
    re_f = round(float(raio_eixo_estribo), 4)
    rb_f = round(float(d_barra_sel / 2), 4)
    
    angulos_math = [i * (2 * math.pi / int(n_barras)) for i in range(int(n_barras))]
    
    # ==========================================
    # 2. SEÇÃO 1: SOLO (Posição 0, 0)
    # ==========================================
    
    # 2.1 Hachura de Concreto (Fundo)
    h_solo = msp.add_hatch(color=256, dxfattribs={'layer': 'CIVIL-254'})
    h_solo.paths.add_edge_path().add_ellipse(center=(0.0, 0.0), major_axis=(rs_f, 0.0), ratio=1.0)

    # 2.2 Contornos e Estrutura
    msp.add_circle((0.0, 0.0), rs_f, dxfattribs={'layer': 'FORMA_02'})
    msp.add_circle((0.0, 0.0), rrev_s_f, dxfattribs={'layer': 'REVESTIMENTO'})
    msp.add_circle((0.0, 0.0), re_f, dxfattribs={'layer': 'ARMADURA'})
    
    # 2.3 Armaduras Longitudinais (Círculo + Hachura na layer FERRO_05)
    for a in angulos_math:
        bx = round(float(raio_centro_barra * math.cos(a)), 4)
        by = round(float(raio_centro_barra * math.sin(a)), 4)
        
        h_bar = msp.add_hatch(color=256, dxfattribs={'layer': 'FERRO_05'})
        h_bar.paths.add_edge_path().add_ellipse(center=(bx, by), major_axis=(rb_f, 0.0), ratio=1.0)
        msp.add_circle((bx, by), rb_f, dxfattribs={'layer': 'FERRO_05'})
        
    # 2.4 Cota e Textos
    msp.add_linear_dim(
        base=(-rs_f - 150.0, 0.0), 
        p1=(0.0, rs_f), 
        p2=(0.0, -rs_f), 
        dimstyle="TICK-1_10", 
        angle=90,
        override={
            "dimtxt": 1.5, 
            "dimpost": "%%c<>" 
        }
    ).render()

    msp.add_text("%%USEÇÃO EM SOLO", dxfattribs={'layer': 'CIVIL-TX5', 'style': '140CL-1_10', 'height': 35}
                ).set_placement((-rs_f, -rs_f - 60.0))
    
    msp.add_text("ESC.1:10", dxfattribs={'layer': 'CIVIL-TX2', 'style': '80CL-1_10', 'height': 20}
                ).set_placement((-rs_f, -rs_f - 100.0))
    
    # ==========================================
    # 3. SEÇÃO 2: ROCHA (Posição 1000, 0)
    # ==========================================
    offset_r = 1000.0

    # 3.1 Hachura de Concreto (Fundo)
    h_rocha = msp.add_hatch(color=256, dxfattribs={'layer': 'CIVIL-254'})
    h_rocha.paths.add_edge_path().add_ellipse(center=(offset_r, 0.0), major_axis=(rr_f, 0.0), ratio=1.0)

    # 3.2 Contornos e Estrutura
    msp.add_circle((offset_r, 0.0), rr_f, dxfattribs={'layer': 'FORMA_02'})
    msp.add_circle((offset_r, 0.0), rr_f, dxfattribs={'layer': 'REVESTIMENTO'})
    msp.add_circle((offset_r, 0.0), re_f, dxfattribs={'layer': 'ARMADURA'})
    
    # 3.3 Armaduras Longitudinais (Círculo + Hachura na layer FERRO_05)
    for a in angulos_math:
        bx = round(float(raio_centro_barra * math.cos(a)), 4)
        by = round(float(raio_centro_barra * math.sin(a)), 4)
        
        h_bar_r = msp.add_hatch(color=256, dxfattribs={'layer': 'FERRO_05'})
        h_bar_r.paths.add_edge_path().add_ellipse(center=(offset_r + bx, by), major_axis=(rb_f, 0.0), ratio=1.0)
        msp.add_circle((offset_r + bx, by), rb_f, dxfattribs={'layer': 'FERRO_05'})
        
    # 3.4 Cota e Textos
    msp.add_linear_dim(
        base=(offset_r - rr_f - 150.0, 0.0), 
        p1=(offset_r, rr_f), 
        p2=(offset_r, -rr_f), 
        dimstyle="TICK-1_10", 
        angle=90,
        override={
            "dimpost": "%%c<>",
            "dimtad": 1,  # Força o texto a ficar ACIMA da linha (Vertical: Above)
            "dimjust": 0  # Força o texto a ficar CENTRALIZADO (Horizontal: Centered)
        }
    ).render()

    msp.add_text("%%USEÇÃO EM ROCHA", dxfattribs={'layer': 'CIVIL-TX5', 'style': '140CL-1_10', 'height': 35}
                ).set_placement((offset_r - rr_f, -rr_f - 60.0))
    
    msp.add_text("ESC.1:10", dxfattribs={'layer': 'CIVIL-TX2', 'style': '80CL-1_10', 'height': 20}
                ).set_placement((offset_r - rr_f, -rr_f - 100.0))
    
    # ==========================================
    # 4. PERFIL LONGITUDINAL (Posição 0, 2000)
    # ==========================================
    offset_p = 2000.0
    l_solo_mm = l_solo * 1000
    l_rocha_mm = l_rocha * 1000
    l_espera_mm = l_espera * 1000
    passo_est_mm = passo_estribo * 10 
    
    y_inicio = 0.0
    y_rocha_fim = l_rocha_mm
    y_topo = l_rocha_mm + l_solo_mm 
    y_topo_com_espera = y_topo + l_espera_mm 
    
    # Cobrimentos mínimo (5cm = 50mm)
    covering_bottom_mm = 50.0
    covering_top_mm = 50.0
    
    # Limites da armadura
    y_armadura_inicio = y_inicio + covering_bottom_mm
    y_armadura_topo = y_topo - covering_top_mm  # Estribo para na estaca, não entra no bloco
    y_armadura_topo_barras = y_topo_com_espera - covering_top_mm  # Barras entram no bloco 
    
    # 4.1 Contornos Perfil - Contorno único da estaca
    # Desenhar um único contorno fechado para evitar linha de separação
    pile_outline = [
        (offset_p - rr_f, y_inicio),      # Fundo esquerdo rocha
        (offset_p + rr_f, y_inicio),      # Fundo direito rocha
        (offset_p + rr_f, y_rocha_fim),   # Topo direito rocha
        (offset_p + rrev_s_f, y_rocha_fim), # Transição direita para solo
        (offset_p + rrev_s_f, y_topo),    # Topo direito solo
        (offset_p - rrev_s_f, y_topo),    # Topo esquerdo solo
        (offset_p - rrev_s_f, y_rocha_fim), # Transição esquerda para rocha
        (offset_p - rr_f, y_rocha_fim),   # Topo esquerdo rocha
        (offset_p - rr_f, y_inicio)       # Volta ao início
    ]
    msp.add_lwpolyline(pile_outline, dxfattribs={'layer': 'PERFIL'})
    
    # 4.2 Barras Longitudinais no Perfil
    for a in angulos_math:
        pos_x = offset_p + (raio_centro_barra * math.cos(a))
        msp.add_line((pos_x, y_armadura_inicio), (pos_x, y_armadura_topo_barras), dxfattribs={'layer': 'FERRO_05'})
    
    # 4.3 Espiral (Zigue-Zague) - Apenas na estaca, não no bloco
    y_ptr = y_armadura_inicio
    pts_esp = []
    half_step = passo_est_mm / 2
    
    # Perna inicial horizontal
    pts_esp.append((offset_p - re_f, y_ptr))
    pts_esp.append((offset_p + re_f, y_ptr))
    
    lado_esq = True
    y_ptr += half_step
    
    while y_ptr <= y_armadura_topo:
        x_pt = offset_p - re_f if lado_esq else offset_p + re_f
        pts_esp.append((x_pt, y_ptr))
        lado_esq = not lado_esq
        y_ptr += half_step
    
    # Perna final horizontal
    if pts_esp:
        ux, uy = pts_esp[-1]
        pts_esp.append((offset_p + re_f if ux < offset_p else offset_p - re_f, uy))
    
    if pts_esp:
        msp.add_lwpolyline(pts_esp, dxfattribs={'layer': 'ARMADURA'})
    
    # ==========================================
    # 4.4 Esquema de Armação (Trespasse)
    # ==========================================
    offset_scheme = offset_p + 600.0
    l_teorico_mm = (l_solo + l_rocha - 0.15 + l_espera) * 1000  # Mesmo cálculo de l_teorico_barra em mm
    
    if l_teorico_mm > 12000:
        trespasse_mm = 50 * d_barra_sel
        offset_x = 100.0  # Deslocamento horizontal para indicar justaposição
        
        # Desenhar segmentos de 12m com trespasses, respeitando cobrimentos
        num_segmentos = math.ceil(l_teorico_mm / 12000)
        for i in range(num_segmentos):
            y_start = y_armadura_inicio + i * 12000 - i * trespasse_mm
            y_end = min(y_armadura_inicio + (i + 1) * 12000 - i * trespasse_mm, y_armadura_topo_barras)
            x_offset = offset_scheme + (i % 2) * offset_x
            msp.add_line((x_offset, y_start), (x_offset, y_end), dxfattribs={'layer': 'FERRO_05'})
        
        # Título do esquema
        msp.add_text("ESQUEMA DE ARMAÇÃO", dxfattribs={'layer': 'CIVIL-TX5', 'style': '140CL-1_10', 'height': 35}
                    ).set_placement((offset_scheme - 50, y_topo_com_espera + 100))
        
        # Nota sobre trespasses
        nota = f"NOTAS: Comprimento total da estaca excede 12m. Emendas longitudinais por trespasse de 50Ø, representadas esquematicamente. Garantir defasagem ao longo do fuste conforme NBR 6118."
        msp.add_text(nota, dxfattribs={'layer': 'CIVIL-TX2', 'style': '80CL-1_10', 'height': 20}
                    ).set_placement((offset_scheme - 50, y_topo_com_espera + 50))
    
    # ==========================================
    # 5. SALVAMENTO
    # ==========================================
    if return_bytes:
        # Modo Streamlit: usa texto em memória e depois retorna bytes
        buffer = io.StringIO()
        doc.write(buffer)
        return buffer.getvalue().encode('utf-8')
    else:
        # Modo disco: salva o arquivo
        if caminho_pasta is None:
            caminho_pasta = os.getcwd()
        
        caminho_final = os.path.join(caminho_pasta, f"{nome_arquivo}.dxf")
        doc.saveas(caminho_final)
        
        return caminho_final