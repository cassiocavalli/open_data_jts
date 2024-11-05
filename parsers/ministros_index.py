from typing import Dict, Set, Optional
from collections import defaultdict
import json
import csv
import os
from pathlib import Path

class MinistrosIndex:
    """Índice para análise de ministros e suas variações de nome."""
    
    def __init__(self):
        # Estruturas para indexação
        self.ministros: Dict[str, Dict] = {}  # nome padrão -> info do ministro
        self.variacoes: Dict[str, str] = {}  # variação -> nome padrão
        self.by_status: Dict[str, Set[str]] = defaultdict(set)  # status -> set de nomes
        
        # Carrega dados do CSV
        self._load_csv()
        
    def _load_csv(self, csv_path: Optional[str] = None) -> None:
        """Carrega dados do CSV de ministros."""
        if not csv_path:
            csv_path = os.path.join(os.path.dirname(__file__), 'data', 'ministros.csv')
            
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    nome = row['nomeMinistro'].strip()
                    status = row['statusMinistro'].strip()
                    
                    self.ministros[nome] = {
                        'nome': nome,
                        'status': status,
                        'variacoes': set()
                    }
                    
                    self.by_status[status].add(nome)
                    
                    # Adiciona variações comuns
                    self._add_variations(nome)
                    
        except Exception as e:
            print(f"Erro ao carregar CSV de ministros: {str(e)}")
            
    def _add_variations(self, nome: str) -> None:
        """Adiciona variações comuns do nome do ministro."""
        partes = nome.split()
        
        # Nome completo é uma variação
        self.variacoes[nome] = nome
        self.ministros[nome]['variacoes'].add(nome)
        
        # Primeira + última parte
        if len(partes) > 1:
            variacao = f"{partes[0]} {partes[-1]}"
            self.variacoes[variacao] = nome
            self.ministros[nome]['variacoes'].add(variacao)
            
        # Iniciais + última parte
        if len(partes) > 2:
            iniciais = ''.join(p[0] + '.' for p in partes[:-1])
            variacao = f"{iniciais} {partes[-1]}"
            self.variacoes[variacao] = nome
            self.ministros[nome]['variacoes'].add(variacao)
            
    def get_nome_padrao(self, nome: str) -> Optional[str]:
        """Retorna o nome padrão dado uma variação."""
        nome = nome.strip()
        return self.variacoes.get(nome)
        
    def get_status(self, nome: str) -> Optional[str]:
        """Retorna o status do ministro dado seu nome ou variação."""
        nome_padrao = self.get_nome_padrao(nome)
        if nome_padrao:
            return self.ministros[nome_padrao]['status']
        return None
        
    def process_directory(self, base_path: str) -> None:
        """Processa diretório para encontrar novas variações de nomes."""
        print("\nAnalisando variações de nomes de ministros...")
        
        total_files = 0
        processed_files = 0
        new_variations = set()
        
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
                            relator = acordao.get('ministroRelator', '').strip()
                            if relator and relator not in self.variacoes:
                                new_variations.add(relator)
                                
                        processed_files += 1
                        if processed_files % 100 == 0:
                            print(f"Processados {processed_files}/{total_files} arquivos")
                            
                    except Exception as e:
                        print(f"Erro ao processar {filepath}: {str(e)}")
                        
        if new_variations:
            print("\nNovas variações de nomes encontradas:")
            for var in sorted(new_variations):
                print(f"- {var}")
                
    def save_to_file(self, output_path: str) -> None:
        """Salva o índice em arquivo JSON."""
        index_data = {
            'ministros': {
                nome: {
                    'nome': info['nome'],
                    'status': info['status'],
                    'variacoes': list(info['variacoes'])
                }
                for nome, info in self.ministros.items()
            },
            'variacoes': self.variacoes,
            'by_status': {k: list(v) for k, v in self.by_status.items()}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
            
        print(f"\nÍndice salvo em: {output_path}")

def main():
    input_path = r"D:\Dropbox\Github\Dados Abertos STJ\Espelhos de Acordaos Parseados"
    output_path = r"D:\Dropbox\Github\Dados Abertos STJ\indices\ministros.json"
    
    # Garante que o diretório de saída existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    index = MinistrosIndex()
    index.process_directory(input_path)
    index.save_to_file(output_path)

if __name__ == "__main__":
    main()