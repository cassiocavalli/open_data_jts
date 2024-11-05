import os
from typing import Dict, Tuple, Optional
from .json_utils import process_json_content

class AcordaoIndex:
    """Índice para localizar IDs de acórdãos por tipo e número."""
    
    def __init__(self):
        self._index: Dict[Tuple[str, str], str] = {}  # (tipo, numero) -> id
        
    def add_acordao(self, acordao: dict) -> None:
        """Adiciona um acórdão ao índice."""
        if not acordao.get('id'):
            return
            
        tipo = acordao.get('siglaClasse', '').strip()
        numero = acordao.get('numeroProcesso', '').strip()
        
        if tipo and numero:
            self._index[(tipo, numero)] = acordao['id']
            
    def get_id(self, tipo: str, numero: str) -> Optional[str]:
        """Retorna o ID do acórdão dado seu tipo e número."""
        tipo = tipo.strip()
        numero = numero.strip()
        return self._index.get((tipo, numero))
        
    def build_from_directory(self, base_path: str) -> None:
        """Constrói o índice a partir de um diretório com arquivos JSON."""
        total_files = 0
        processed_files = 0
        
        print("\nConstruindo índice de acórdãos...")
        
        for root, _, files in os.walk(base_path):
            if os.path.basename(root).startswith("Espelho"):
                json_files = [f for f in files if f.endswith('.json')]
                total_files += len(json_files)
                
                for filename in json_files:
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        acordaos = process_json_content(content)
                        if acordaos:
                            if not isinstance(acordaos, list):
                                acordaos = [acordaos]
                                
                            for acordao in acordaos:
                                self.add_acordao(acordao)
                                
                            processed_files += 1
                            
                            if processed_files % 100 == 0:
                                print(f"Indexados {processed_files}/{total_files} arquivos")
                                
                    except Exception as e:
                        print(f"Erro ao indexar arquivo {filepath}: {str(e)}")
                        continue
                        
        print(f"\nÍndice construído com sucesso! {processed_files}/{total_files} arquivos processados")