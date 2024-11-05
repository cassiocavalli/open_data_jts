import re
from datetime import datetime
from typing import Dict, Optional

def parse_data_publicacao(data_string: str) -> Dict[str, Optional[str]]:
    """Parse a string de data de publicação no formato STJ."""
    resultado = {
        "meioPub": None,
        "dataPublicacao": None,
        "paginaPublicacao": None
    }
    
    try:
        # Extrai o meio de publicação (primeiro campo antes de espaços)
        meio_pub = data_string.strip().split()[0]
        resultado["meioPub"] = meio_pub
        
        # Extrai a data usando regex
        data_match = re.search(r'DATA:(\d{2}/\d{2}/\d{4})', data_string)
        if data_match:
            data_str = data_match.group(1)
            # Converte para formato SQL (YYYY-MM-DD)
            data_obj = datetime.strptime(data_str, '%d/%m/%Y')
            resultado["dataPublicacao"] = data_obj.strftime('%Y-%m-%d')
            
        # Extrai a página usando regex
        pagina_match = re.search(r'PG:(\d+)', data_string)
        if pagina_match:
            resultado["paginaPublicacao"] = pagina_match.group(1)
            
    except Exception as e:
        print(f"Erro ao processar data de publicação: {str(e)}")
        
    return resultado