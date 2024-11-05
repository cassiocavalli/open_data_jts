import re
from typing import Dict, List, Optional
from .acordao_index import AcordaoIndex

def parse_jurisprudencia_citada(jurisprudencia: str, index: Optional[AcordaoIndex] = None) -> Dict[str, List[Dict]]:
    """
    Parse jurisprudência citada no formato STJ.
    
    Args:
        jurisprudencia: String contendo a jurisprudência citada
        index: Índice opcional para localizar IDs dos acórdãos citados
        
    Returns:
        Dicionário com as categorias e acórdãos citados
    """
    resultado = {"categorias": []}
    
    if not jurisprudencia:
        return resultado
        
    try:
        categoria_atual = None
        acordaos_atuais = []
        tribunal_atual = None
        
        linhas = [l.strip() for l in jurisprudencia.split('\n') if l.strip()]
        
        for linha in linhas:
            # Se é uma nova categoria (começa com parênteses)
            if linha.startswith('('):
                # Se já temos uma categoria sendo processada, salvamos ela
                if categoria_atual and acordaos_atuais:
                    categoria_atual["acordaosCitados"] = acordaos_atuais
                    resultado["categorias"].append(categoria_atual)
                    acordaos_atuais = []
                
                # Extrai a nova categoria
                match_categoria = re.match(r'\((.*?)\)', linha)
                if match_categoria:
                    categorias = [cat.strip() for cat in match_categoria.group(1).split('-')]
                    categoria_atual = {
                        "categoriaPrincipal": categorias[0],
                        "subcategorias": categorias[1:] if len(categorias) > 1 else []
                    }
            
            # Se não começa com parênteses, processa como citação de acórdão
            else:
                # Identifica tribunal no início da linha
                match_tribunal = re.match(r'(STJ|STF)\s*-\s*', linha)
                if match_tribunal:
                    tribunal_atual = match_tribunal.group(1)
                    resto_linha = linha[match_tribunal.end():].strip()
                    
                    # Para cada citação na linha
                    for citacao in re.split(r',\s*(?=<<|STJ|STF|REPERCUSSÃO|SÚMULA|TEMA)', resto_linha):
                        citacao = citacao.strip()
                        if not citacao:
                            continue
                        
                        # Tenta encontrar padrão <<TIPO NUMERO>>-UF
                        match_padrao = re.search(r'<<([^>]+)>>-(\w+)', citacao)
                        if match_padrao:
                            recurso_completo = match_padrao.group(1)
                            estado = match_padrao.group(2)
                            
                            # Separa tipo e número
                            partes = recurso_completo.split()
                            numero = partes[-1]
                            tipo = ' '.join(partes[:-1]) if len(partes) > 1 else partes[0]
                            
                            acordao = {
                                "tribunal": tribunal_atual,
                                "tipo": tipo,
                                "numero": numero,
                                "estado": estado
                            }
                            
                            # Procura por informações adicionais entre parênteses
                            match_info = re.search(r'\((.*?)\)', citacao)
                            if match_info:
                                info = match_info.group(1).strip()
                                
                                # Verifica se é recurso repetitivo
                                if "RECURSO REPETITIVO" in info:
                                    acordao["recursoRepetitivo"] = True
                                    
                                    # Extrai temas
                                    match_temas = re.search(r'TEMA\(s\)\s*(\d+(?:\s*,\s*\d+)*)', info)
                                    if match_temas:
                                        temas = [tema.strip() for tema in match_temas.group(1).split(',')]
                                        acordao["temas"] = temas
                            
                            # Tenta localizar o ID do acórdão no índice
                            if index and tribunal_atual == "STJ":
                                acordao_id = index.get_id(tipo, numero)
                                if acordao_id:
                                    acordao["id"] = acordao_id
                            
                            acordaos_atuais.append(acordao)
                            
                        # Tenta encontrar padrão de REPERCUSSÃO GERAL ou outros
                        else:
                            match_especial = re.search(r'(REPERCUSSÃO GERAL|SÚMULA|TEMA)\s*-?\s*(?:TEMA\(?S?\)?\s*)?(\d+)', citacao)
                            if match_especial:
                                tipo = match_especial.group(1)
                                numero = match_especial.group(2)
                                
                                acordao = {
                                    "tribunal": tribunal_atual,
                                    "tipo": tipo,
                                    "numero": numero
                                }
                                
                                acordaos_atuais.append(acordao)
        
        # Não esquecer de adicionar a última categoria processada
        if categoria_atual and acordaos_atuais:
            categoria_atual["acordaosCitados"] = acordaos_atuais
            resultado["categorias"].append(categoria_atual)
    
    except Exception as e:
        print(f"Erro ao processar jurisprudência citada: {str(e)}")
    
    return resultado