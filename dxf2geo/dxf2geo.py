import ezdxf
import numpy as np

def extrair_geometria_dxf(arquivo_dxf):
    doc = ezdxf.readfile(arquivo_dxf)
    msp = doc.modelspace()
    
    pontos = []
    polilinhas = []
    materiais = []
    
    for entity in msp:
        if entity.dxftype() == 'POLYLINE':
            polyline_points = []
            for vertex in entity.vertices:
                ponto = np.array([vertex.dxf.location.x, vertex.dxf.location.y, vertex.dxf.location.z])
                if ponto.tolist() not in pontos:
                    pontos.append(ponto.tolist())
                polyline_points.append(pontos.index(ponto.tolist()))
            polilinhas.append(polyline_points)
            materiais.append(entity.dxf.layer)
    
    return np.array(pontos), polilinhas, materiais

def transladar_para_origem(pontos):
    min_x = np.min(pontos[:, 0])
    min_y = np.min(pontos[:, 1])
    
    pontos[:, 0] -= min_x
    pontos[:, 1] -= min_y
    
    return pontos

def criar_geo_arquivo(pontos, polilinhas, nome_arquivo_geo, refino):
    pontos = np.round(pontos, decimals=4)
    with open(nome_arquivo_geo, 'w') as f:
        # Definir a variável de refinamento
        f.write(f'lc = {refino};\n')
        
        # Escrever pontos
        for i, ponto in enumerate(pontos):
            f.write(f'Point({i + 1}) = {{{ponto[0]}, {ponto[1]}, 0.0, lc}};\n')
        
        # Escrever linhas
        linha_id = 1
        line_loops = []
        for i, polyline in enumerate(polilinhas):
            linha_ids = []
            for j in range(len(polyline) - 1):
                f.write(f'Line({linha_id}) = {{{polyline[j] + 1}, {polyline[j + 1] + 1}}};\n')
                linha_ids.append(linha_id)
                linha_id += 1
            line_loops.append(linha_ids)
        
        # Criar superfícies
        for i, linha_ids in enumerate(line_loops):
            f.write(f'Line Loop({i + 1}) = {{{", ".join(map(str, linha_ids))}}};\n')
            f.write(f'Plane Surface({i + 1}) = {{{i + 1}}};\n')

# Nome do arquivo DXF
arquivo_dxf = "nmats3.dxf"
nome_arquivo_geo = "nmats3.geo"
refino = 100  # Valor de refinamento da malha

# Extrair geometria do arquivo DXF
pontos, polilinhas, materiais = extrair_geometria_dxf(arquivo_dxf)

# Transladar pontos para a origem (0, 0)
pontos = transladar_para_origem(pontos)

# Arredondar pontos para 4 casas decimais
pontos = np.round(pontos, decimals=4)

# Criar arquivo .geo para Gmsh
criar_geo_arquivo(pontos, polilinhas, nome_arquivo_geo, refino)

print(f'Arquivo {nome_arquivo_geo} criado com sucesso.')