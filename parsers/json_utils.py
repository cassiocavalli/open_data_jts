import json
from typing import Any, Optional

def process_json_content(content: str) -> Optional[Any]:
    """
    Processa conteúdo JSON com tratamento robusto de erros.
    
    Args:
        content: String contendo JSON
        
    Returns:
        Conteúdo JSON parseado ou None em caso de erro
    """
    try:
        # Remove BOM se presente
        if content.startswith('\ufeff'):
            content = content[1:]
            
        # Limpa espaços e quebras de linha extras
        content = content.strip()
        
        # Garante que é um array JSON válido
        if not content.startswith('['):
            content = '[' + content
        if not content.endswith(']'):
            content = content + ']'
            
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"\nTentando recuperar JSON válido...")
            
            # Tenta encontrar objetos JSON válidos
            valid_objects = []
            current_object = ""
            bracket_count = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(content):
                current_object += char
                
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        bracket_count += 1
                    elif char == '}':
                        bracket_count -= 1
                        if bracket_count == 0:
                            try:
                                obj = json.loads(current_object)
                                valid_objects.append(obj)
                            except:
                                pass
                            current_object = ""
            
            if valid_objects:
                print(f"Recuperados {len(valid_objects)} objetos válidos")
                return valid_objects
                
            print(f"Não foi possível recuperar objetos JSON válidos")
            return None
            
    except Exception as e:
        print(f"Erro ao processar JSON: {str(e)}")
        return None