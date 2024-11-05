import re
from typing import Dict, List

def parse_referencias_legislativas(referencias: List[str]) -> List[Dict]:
    """Parse referências legislativas no formato STJ."""
    resultado = []
    
    if not referencias:
        return resultado
        
    # Lista completa de tipos de referência
    TIPOS_REFERENCIA = {
        'LCP', 'DEL', 'LEI', 'CFB', 'RGI', 'MPR', 'EMC', 'RES', 'ATO', 'PRT', 'SUM'
    }
    
    for ref in referencias:
        try:
            ref_dict = {}
            linhas = [l.strip() for l in ref.split('\n') if l.strip()]
            
            if not linhas:
                continue
                
            # Primeira linha - informações básicas da lei
            primeira_linha = linhas[0].split()
            
            # Processa cada parte da primeira linha
            for parte in primeira_linha:
                if ':' not in parte:
                    continue
                    
                chave, valor = parte.split(':', 1)
                if chave == 'LEG':
                    ref_dict['LEG'] = valor
                elif chave in TIPOS_REFERENCIA:
                    ref_dict['tipo'] = chave
                    # Alguns tipos não têm número
                    if chave not in ['CFB', 'RGI']:
                        ref_dict['numero'] = valor
                elif chave == 'ANO':
                    ref_dict['ANO'] = valor
            
            # Processa órgão emissor (entre parênteses na última linha)
            if linhas[-1].startswith('(') and linhas[-1].endswith(')'):
                ref_dict['orgaoEmissor'] = linhas[-1].strip('()')
                # Remove a última linha se ela contiver apenas o órgão emissor
                if len(linhas) > 1:
                    linhas = linhas[:-1]
            
            # Segunda linha - nome e sigla da lei
            for linha in linhas[1:]:
                if '*****' in linha:
                    partes = linha.split('*****', 1)
                    if len(partes) > 1:
                        resto = partes[1].strip()
                        primeira_palavra = resto.split(maxsplit=1)
                        if primeira_palavra:
                            ref_dict['legSigla'] = primeira_palavra[0]
                            if len(primeira_palavra) > 1:
                                ref_dict['legExtenso'] = primeira_palavra[1]
                    break
            
            # Procura por número de súmula
            for linha in linhas:
                if 'SUM:' in linha:
                    match = re.search(r'SUM:(\d+)', linha)
                    if match:
                        ref_dict['numeroSumula'] = match.group(1)
                        break
            
            # Última linha não-parênteses - artigos e detalhes
            ultima_linha = ''
            for linha in reversed(linhas):
                if not linha.startswith('('):
                    ultima_linha = linha
                    break
                    
            if ultima_linha:
                partes = re.findall(r'([A-Z]+):([^\s]+)', ultima_linha)
                
                art_atual = {}
                detalhes_atual = {}
                contador_art = 0
                
                for chave, valor in partes:
                    if chave == 'ART':
                        # Salva artigo anterior se existir
                        if art_atual:
                            if detalhes_atual:
                                art_atual['detalhes'] = detalhes_atual
                            chave_art = 'ART' if contador_art == 0 else f'ART{contador_art+1}'
                            ref_dict[chave_art] = art_atual.copy()
                        
                        # Inicia novo artigo
                        contador_art += 1
                        art_atual = {'numero': valor}
                        detalhes_atual = {}
                    elif chave in ['PAR', 'INC', 'LET', 'ITEM', 'NUM']:
                        detalhes_atual[chave] = valor
                
                # Salva o último artigo
                if art_atual:
                    if detalhes_atual:
                        art_atual['detalhes'] = detalhes_atual
                    chave_art = 'ART' if contador_art == 1 else f'ART{contador_art}'
                    ref_dict[chave_art] = art_atual
            
            # Só adiciona ao resultado se tiver pelo menos LEG e ANO
            if 'LEG' in ref_dict and 'ANO' in ref_dict:
                resultado.append(ref_dict)
            
        except Exception as e:
            print(f"Erro ao processar referência: {str(e)}")
            continue
    
    return resultado