import re
from datetime import datetime
from typing import Dict, List

def parse_acordaos_similares(acordaos: List[str]) -> Dict[str, Dict[str, str]]:
    """Parse acordãos similares no formato STJ."""
    resultado = {}
    
    if not acordaos:
        return resultado
        
    for idx, acordao in enumerate(acordaos, 1):
        try:
            # Divide em linhas e limpa espaços extras
            linhas = [l.strip() for l in acordao.split('\n') if l.strip()]
            if not linhas:
                continue
            
            # Processa primeira linha
            primeira_linha = ' '.join(linhas[0].split())  # Normaliza espaços
            
            # Extrai número do registro (XXXX/XXXXXXXX-X)
            match_registro = re.search(r'(\d{4}/\d{7}-\d)', primeira_linha)
            if not match_registro:
                continue
                
            registro = match_registro.group(1)
            texto_antes = primeira_linha[:match_registro.start()].strip()
            
            # Extrai tipo, número e estado
            partes = texto_antes.split()
            if len(partes) < 3:
                continue
                
            estado = partes[-1]
            numero = partes[-2]
            tipo = ' '.join(partes[:-2])
            
            # Extrai data da decisão
            data_decisao = None
            match_decisao = re.search(r'Decisão:(\d{2}/\d{2}/\d{4})', primeira_linha)
            if match_decisao:
                try:
                    data_obj = datetime.strptime(match_decisao.group(1), '%d/%m/%Y')
                    data_decisao = data_obj.strftime('%Y-%m-%d')
                except ValueError:
                    pass
                    
            # Processa segunda linha (publicações)
            publicacoes = []
            for linha in linhas[1:]:
                if not linha:
                    continue
                    
                partes_pub = linha.split()
                if partes_pub:
                    fonte = partes_pub[0].strip()
                    
                    match_data = re.search(r'DATA:(\d{2}/\d{2}/\d{4})', linha)
                    data_pub = None
                    if match_data:
                        try:
                            data_obj = datetime.strptime(match_data.group(1), '%d/%m/%Y')
                            data_pub = data_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            pass
                    
                    match_pg = re.search(r'PG:(\d+)', linha)
                    pagina = match_pg.group(1) if match_pg else None
                    
                    pub = {
                        "fonte": fonte,
                        "data": data_pub,
                        "pagina": pagina
                    }
                    publicacoes.append(pub)
            
            # Monta o dicionário do acórdão
            acordao_dict = {
                "tribunal": "STJ",
                "tipo": tipo.strip(),
                "numero": numero,
                "estado": estado,
                "registro": registro
            }
            
            if data_decisao:
                acordao_dict["data_decisao"] = data_decisao
                
            if publicacoes:
                acordao_dict["publicacoes"] = publicacoes
            
            resultado[f"acordaoSimilar{idx}"] = acordao_dict
            
        except Exception as e:
            print(f"Erro ao processar acórdão similar {idx}: {str(e)}")
            continue
    
    return resultado