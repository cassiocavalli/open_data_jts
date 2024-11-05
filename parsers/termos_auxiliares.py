import re
from typing import List, Optional

def parse_termos_auxiliares(termos: str) -> Optional[List[str]]:
    """
    Parse termos auxiliares no formato STJ.
    
    Args:
        termos: String contendo os termos auxiliares
        
    Returns:
        Lista de termos auxiliares ou None se não houver termos
    """
    if not termos or termos == "null":
        return None
        
    resultado = []
    
    try:
        # Remove "MULTA DE" e outros prefixos comuns
        termos = re.sub(r'^MULTA DE\s+', '', termos, flags=re.IGNORECASE)
        
        # Divide por ponto e vírgula ou ponto final
        termos_split = [t.strip() for t in termos.replace(';', '.').split('.')]
        
        # Limpa e adiciona cada termo não vazio
        for termo in termos_split:
            if termo:
                # Remove parênteses e seu conteúdo
                termo = re.sub(r'\([^)]*\)', '', termo).strip()
                if termo:
                    resultado.append(termo)
                
    except Exception as e:
        print(f"Erro ao processar termos auxiliares: {str(e)}")
        
    return resultado if resultado else None