from typing import Dict, List, Set, Optional
from collections import defaultdict
import json
import os
from pathlib import Path

class RelatorIndex:
    """Índice para análise de relatores e citações entre eles."""
    
    def __init__(self):
        # Estruturas para indexação
        self.by_relator: Dict[str, Set[str]] = defaultdict(set)  # relator -> set de IDs de acórdãos
        self.citations: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))  # relator -> relator_citado -> set de IDs
        self.by_year: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))  # ano -> relator -> set de IDs
        self.by_orgao: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))  # órgão -> relator -> set de IDs
        
        # Contadores para estatísticas
        self.total_acordaos = 0
        self.total_citations = 0
        self.unique_relatores = set()
        
    def add_acordao(self, acordao: dict) -> None:
        """Adiciona um acórdão ao índice."""
        if not acordao.get('id') or not acordao.get('ministroRelator'):
            return
            
        acordao_id = acordao['id']
        relator = acordao['ministroRelator'].strip().upper()
        self.unique_relatores.add(relator)
        
        # Indexa por relator
        self.by_relator[relator].add(acordao_id)
        
        # Indexa por ano (se disponível)
        if 'dataDecisao' in acordao:
            ano = acordao['dataDecisao'][:4]  # Primeiros 4 dígitos
            self.by_year[ano][relator].add(acordao_id)
            
        # Indexa por órgão julgador
        if 'nomeOrgaoJulgador' in acordao:
            orgao = acordao['nomeOrgaoJulgador'].strip().upper()
            self.by_orgao[orgao][relator].add(acordao_id)
            
        # Processa citações na jurisprudência
        jurisprudencia = acordao.get('jurisprudenciaCitadaEstruturada', {})
        for categoria in jurisprudencia.get('categorias', []):
            for citacao in categoria.get('acordaosCitados', []):
                if citacao.get('id'):  # Se temos o ID do acórdão citado
                    self.total_citations += 1
                    # Adiciona a citação ao índice de citações
                    self.citations[relator][citacao['id']].add(acordao_id)
        
        self.total_acordaos += 1
        
    def process_directory(self, base_path: str) -> None:
        """Processa todos os arquivos JSON do diretório."""
        print("\nConstruindo índice de relatores...")
        
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
                            self.add_acordao(acordao)
                                
                        processed_files += 1
                        if processed_files % 100 == 0:
                            print(f"Processados {processed_files}/{total_files} arquivos")
                            
                    except Exception as e:
                        print(f"Erro ao processar {filepath}: {str(e)}")
                        
        self._generate_report()
        
    def _generate_report(self) -> None:
        """Gera relatório com estatísticas do índice."""
        report = f"""
=== Relatório do Índice de Relatores ===

Estatísticas Gerais:
- Total de acórdãos: {self.total_acordaos:,}
- Total de citações: {self.total_citations:,}
- Relatores únicos: {len(self.unique_relatores):,}

Top 10 Relatores por Número de Acórdãos:
{self._format_top_items(self.by_relator, 10)}

Top 10 Relatores Mais Citados:
{self._format_top_citations(10)}

Top 10 Órgãos por Número de Acórdãos:
{self._format_top_orgaos(10)}
"""
        print(report)
        
    def _format_top_items(self, index: Dict[str, Set[str]], limit: int) -> str:
        """Formata os top items de um índice para o relatório."""
        sorted_items = sorted(index.items(), key=lambda x: len(x[1]), reverse=True)[:limit]
        return '\n'.join(f"- {item}: {len(refs):,} acórdãos" 
                        for item, refs in sorted_items)
                        
    def _format_top_citations(self, limit: int) -> str:
        """Formata os relatores mais citados para o relatório."""
        citation_counts = defaultdict(int)
        for relator_dict in self.citations.values():
            for citacoes in relator_dict.values():
                citation_counts[relator_dict] += len(citacoes)
                
        sorted_items = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return '\n'.join(f"- {item}: {count:,} citações" 
                        for item, count in sorted_items)
                        
    def _format_top_orgaos(self, limit: int) -> str:
        """Formata os órgãos com mais acórdãos para o relatório."""
        orgao_counts = {
            orgao: sum(len(acordaos) for acordaos in relatores.values())
            for orgao, relatores in self.by_orgao.items()
        }
        sorted_items = sorted(orgao_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return '\n'.join(f"- {item}: {count:,} acórdãos" 
                        for item, count in sorted_items)
        
    def save_to_file(self, output_path: str) -> None:
        """Salva o índice em arquivo JSON."""
        index_data = {
            'by_relator': {k: list(v) for k, v in self.by_relator.items()},
            'citations': {k: {k2: list(v2) for k2, v2 in v.items()} 
                         for k, v in self.citations.items()},
            'by_year': {k: {k2: list(v2) for k2, v2 in v.items()}
                       for k, v in self.by_year.items()},
            'by_orgao': {k: {k2: list(v2) for k2, v2 in v.items()}
                        for k, v in self.by_orgao.items()},
            'stats': {
                'total_acordaos': self.total_acordaos,
                'total_citations': self.total_citations,
                'unique_relatores': len(self.unique_relatores)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
            
        print(f"\nÍndice salvo em: {output_path}")

def main():
    input_path = r"D:\Dropbox\Github\Dados Abertos STJ\Espelhos de Acordaos Parseados"
    output_path = r"D:\Dropbox\Github\Dados Abertos STJ\indices\relatores.json"
    
    # Garante que o diretório de saída existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    index = RelatorIndex()
    index.process_directory(input_path)
    index.save_to_file(output_path)

if __name__ == "__main__":
    main()