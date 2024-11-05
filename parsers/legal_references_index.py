from typing import Dict, List, Set, Optional
from collections import defaultdict
import json
import os
from pathlib import Path

class LegalReferencesIndex:
    """Índice para análise de referências legislativas."""
    
    def __init__(self):
        # Estruturas para indexação
        self.by_law: Dict[str, Set[str]] = defaultdict(set)  # lei -> set de IDs de acórdãos
        self.by_article: Dict[str, Set[str]] = defaultdict(set)  # lei+artigo -> set de IDs
        self.by_paragraph: Dict[str, Set[str]] = defaultdict(set)  # lei+artigo+parágrafo -> set de IDs
        self.by_item: Dict[str, Set[str]] = defaultdict(set)  # lei+artigo+item -> set de IDs
        self.by_year: Dict[str, Set[str]] = defaultdict(set)  # ano -> set de IDs
        
        # Contadores para estatísticas
        self.total_references = 0
        self.unique_laws = set()
        self.unique_articles = set()
        
    def add_reference(self, ref: dict, acordao_id: str) -> None:
        """Adiciona uma referência legislativa ao índice."""
        if not ref.get('LEG') or not ref.get('ANO'):
            return
            
        # Identifica a lei
        law_id = f"{ref['LEG']}-{ref['ANO']}"
        self.by_law[law_id].add(acordao_id)
        self.unique_laws.add(law_id)
        
        # Registra o ano
        self.by_year[ref['ANO']].add(acordao_id)
        
        # Processa artigos e seus detalhes
        for key, value in ref.items():
            if key.startswith('ART'):
                if isinstance(value, dict):
                    art_num = value.get('numero')
                    if art_num:
                        # Indexa artigo
                        art_id = f"{law_id}:ART{art_num}"
                        self.by_article[art_id].add(acordao_id)
                        self.unique_articles.add(art_id)
                        
                        # Indexa detalhes do artigo
                        if 'detalhes' in value:
                            for det_type, det_value in value['detalhes'].items():
                                if det_type == 'PAR':
                                    par_id = f"{art_id}:PAR{det_value}"
                                    self.by_paragraph[par_id].add(acordao_id)
                                elif det_type in ('INC', 'ITEM', 'LET'):
                                    item_id = f"{art_id}:{det_type}{det_value}"
                                    self.by_item[item_id].add(acordao_id)
        
        self.total_references += 1
        
    def process_directory(self, base_path: str) -> None:
        """Processa todos os arquivos JSON do diretório."""
        print("\nConstruindo índice de referências legislativas...")
        
        total_files = 0
        processed_files = 0
        
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
                            if 'id' not in acordao:
                                continue
                                
                            refs = acordao.get('referenciasLegislativasEstruturadas', [])
                            for ref in refs:
                                self.add_reference(ref, acordao['id'])
                                
                        processed_files += 1
                        if processed_files % 100 == 0:
                            print(f"Processados {processed_files}/{total_files} arquivos")
                            
                    except Exception as e:
                        print(f"Erro ao processar {filepath}: {str(e)}")
                        
        self._generate_report()
        
    def _generate_report(self) -> None:
        """Gera relatório com estatísticas do índice."""
        report = f"""
=== Relatório do Índice de Referências Legislativas ===

Estatísticas Gerais:
- Total de referências: {self.total_references:,}
- Leis únicas citadas: {len(self.unique_laws):,}
- Artigos únicos citados: {len(self.unique_articles):,}

Top 10 Leis Mais Citadas:
{self._format_top_items(self.by_law, 10)}

Top 10 Artigos Mais Citados:
{self._format_top_items(self.by_article, 10)}

Top 10 Anos com Mais Citações:
{self._format_top_items(self.by_year, 10)}
"""
        print(report)
        
    def _format_top_items(self, index: Dict[str, Set[str]], limit: int) -> str:
        """Formata os top items de um índice para o relatório."""
        sorted_items = sorted(index.items(), key=lambda x: len(x[1]), reverse=True)[:limit]
        return '\n'.join(f"- {item}: {len(refs):,} citações" 
                        for item, refs in sorted_items)
        
    def save_to_file(self, output_path: str) -> None:
        """Salva o índice em arquivo JSON."""
        index_data = {
            'by_law': {k: list(v) for k, v in self.by_law.items()},
            'by_article': {k: list(v) for k, v in self.by_article.items()},
            'by_paragraph': {k: list(v) for k, v in self.by_paragraph.items()},
            'by_item': {k: list(v) for k, v in self.by_item.items()},
            'by_year': {k: list(v) for k, v in self.by_year.items()},
            'stats': {
                'total_references': self.total_references,
                'unique_laws': len(self.unique_laws),
                'unique_articles': len(self.unique_articles)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
            
        print(f"\nÍndice salvo em: {output_path}")

def main():
    input_path = r"D:\Dropbox\Github\Dados Abertos STJ\Espelhos de Acordaos Parseados"
    output_path = r"D:\Dropbox\Github\Dados Abertos STJ\indices\referencias_legislativas.json"
    
    # Garante que o diretório de saída existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    index = LegalReferencesIndex()
    index.process_directory(input_path)
    index.save_to_file(output_path)

if __name__ == "__main__":
    main()