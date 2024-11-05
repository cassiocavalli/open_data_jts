from typing import Dict, Set, Optional
from collections import defaultdict
import json
import csv
import os
from pathlib import Path

class RecursosIndex:
    """Índice para análise de tipos de recursos e suas siglas."""
    
    def __init__(self):
        # Estruturas para indexação
        self.recursos: Dict[str, Dict] = {}  # sigla -> info do recurso
        self.siglas: Dict[str, str] = {}  # sigla alternativa -> sigla padrão
        self.by_tipo: Dict[str, Set[str]] = defaultdict(set)  # tipo -> set de siglas
        
        # Carrega dados do CSV
        self._load_csv()
        
    def _load_csv(self, csv_path: Optional[str] = None) -> None:
        """Carrega dados do CSV de recursos."""
        if not csv_path:
            csv_path = os.path.join(os.path.dirname(__file__), 'data', 'recursos.csv')
            
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sigla = row['siglaRecAbrv'].strip()
                    nome = row['siglaRecExt'].strip()
                    
                    self.recursos[sigla] = {
                        'sigla': sigla,
                        'nome': nome,
                        'alternativas': set()
                    }
                    
                    # Adiciona sigla principal
                    self.siglas[sigla] = sigla
                    self.recursos[sigla]['alternativas'].add(sigla)
                    
                    # Adiciona variações comuns
                    self._add_variations(sigla, nome)
                    
        except Exception as e:
            print(f"Erro ao carregar CSV de recursos: {str(e)}")
            
    def _add_variations(self, sigla: str, nome: str) -> None:
        """Adiciona variações comuns da sigla do recurso."""
        # Remove pontos e espaços
        clean_sigla = sigla.replace('.', '').replace(' ', '')
        self.siglas[clean_sigla] = sigla
        self.recursos[sigla]['alternativas'].add(clean_sigla)
        
        # Adiciona versão com pontos
        if len(sigla) > 1:
            dotted = '.'.join(sigla)
            self.siglas[dotted] = sigla
            self.recursos[sigla]['alternativas'].add(dotted)
            
        # Extrai sigla do nome completo
        palavras = nome.split()
        if len(palavras) > 1:
            sigla_nome = ''.join(p[0] for p in palavras if p[0].isupper())
            if sigla_nome:
                self.siglas[sigla_nome] = sigla
                self.recursos[sigla]['alternativas'].add(sigla_nome)
                
    def get_sigla_padrao(self, sigla: str) -> Optional[str]:
        """Retorna a sigla padrão dada uma variação."""
        sigla = sigla.strip()
        return self.siglas.get(sigla)
        
    def get_nome(self, sigla: str) -> Optional[str]:
        """Retorna o nome completo do recurso dada sua sigla ou variação."""
        sigla_padrao = self.get_sigla_padrao(sigla)
        if sigla_padrao:
            return self.recursos[sigla_padrao]['nome']
        return None
        
    def process_directory(self, base_path: str) -> None:
        """Processa diretório para encontrar novas siglas."""
        print("\nAnalisando siglas de recursos...")
        
        total_files = 0
        processed_files = 0
        new_siglas = set()
        
        for root, _, files in os.walk(base_path):
            if os.path.basename(root).startswith("Espelho"):
                json_files = [f for f in files if f.endswith('.json')]
                total_files += len(json_files)
                
                for filename in json_files:
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            acordaos = json.load(f)
                            
                        if not isinstance(acordaos, list):
                            acordaos = [acordaos]
                            
                        for acordao in acordaos:
                            sigla = acordao.get('siglaClasse', '').strip()
                            if sigla and sigla not in self.siglas:
                                new_siglas.add(sigla)
                                
                        processed_files += 1
                        if processed_files % 100 == 0:
                            print(f"Processados {processed_files}/{total_files} arquivos")
                            
                    except Exception as e:
                        print(f"Erro ao processar {filepath}: {str(e)}")
                        
        if new_siglas:
            print("\nNovas siglas encontradas:")
            for sigla in sorted(new_siglas):
                print(f"- {sigla}")
                
    def save_to_file(self, output_path: str) -> None:
        """Salva o índice em arquivo JSON."""
        index_data = {
            'recursos': {
                sigla: {
                    'sigla': info['sigla'],
                    'nome': info['nome'],
                    'alternativas': list(info['alternativas'])
                }
                for sigla, info in self.recursos.items()
            },
            'siglas': self.siglas
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
            
        print(f"\nÍndice salvo em: {output_path}")

def main():
    input_path = r"D:\Dropbox\Github\Dados Abertos STJ\Espelhos de Acordaos Parseados"
    output_path = r"D:\Dropbox\Github\Dados Abertos STJ\indices\recursos.json"
    
    # Garante que o diretório de saída existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    index = RecursosIndex()
    index.process_directory(input_path)
    index.save_to_file(output_path)

if __name__ == "__main__":
    main()