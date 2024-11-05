import json
import os
from datetime import datetime
from typing import Dict, List, Union
from pathlib import Path

from parsers.data_publicacao import parse_data_publicacao
from parsers.acordaos_similares import parse_acordaos_similares
from parsers.jurisprudencia_citada import parse_jurisprudencia_citada
from parsers.referencias_legislativas import parse_referencias_legislativas
from parsers.complementary_info import parse_complementary_info
from parsers.termos_auxiliares import parse_termos_auxiliares
from parsers.acordao_index import AcordaoIndex
from parsers.json_utils import process_json_content

def process_acordao(acordao: Dict, index: AcordaoIndex) -> Dict:
    """Processa todos os campos de um acórdão"""
    
    # Processa data de publicação
    if 'dataPublicacao' in acordao and acordao['dataPublicacao']:
        acordao['publicacaoEstruturada'] = parse_data_publicacao(acordao['dataPublicacao'])
    
    # Processa jurisprudência citada
    if 'jurisprudenciaCitada' in acordao and acordao['jurisprudenciaCitada']:
        acordao['jurisprudenciaCitadaEstruturada'] = parse_jurisprudencia_citada(
            acordao['jurisprudenciaCitada'],
            index=index
        )
    
    # Processa referências legislativas
    if 'referenciasLegislativas' in acordao and acordao['referenciasLegislativas']:
        acordao['referenciasLegislativasEstruturadas'] = parse_referencias_legislativas(acordao['referenciasLegislativas'])
    
    # Processa acórdãos similares
    if 'acordaosSimilares' in acordao and acordao['acordaosSimilares']:
        acordao['acordaosSimilaresEstruturados'] = parse_acordaos_similares(acordao['acordaosSimilares'])
    
    # Processa informações complementares
    if 'informacoesComplementares' in acordao and acordao['informacoesComplementares']:
        acordao['informacoesComplementaresEstruturadas'] = parse_complementary_info(acordao['informacoesComplementares'])
        
    # Processa termos auxiliares
    if 'termosAuxiliares' in acordao and acordao['termosAuxiliares']:
        acordao['termosAuxiliaresEstruturados'] = parse_termos_auxiliares(acordao['termosAuxiliares'])
    
    return acordao

def process_directory(input_base_path: str, output_base_path: str):
    """Processa todos os arquivos JSON das pastas que começam com 'Espelho'"""
    os.makedirs(output_base_path, exist_ok=True)
    
    total_arquivos = 0
    arquivos_processados = 0
    total_acordaos = 0
    erros = []
    
    inicio = datetime.now()
    
    # Primeiro constrói o índice de todos os acórdãos
    index = AcordaoIndex()
    index.build_from_directory(input_base_path)
    
    # Depois processa os arquivos
    for root, _, files in os.walk(input_base_path):
        if os.path.basename(root).startswith("Espelho"):
            print(f"\nProcessando diretório: {root}")
            
            relative_path = os.path.relpath(root, input_base_path)
            output_dir = os.path.join(output_base_path, relative_path)
            os.makedirs(output_dir, exist_ok=True)
            
            for filename in files:
                if filename.endswith('.json'):
                    total_arquivos += 1
                    input_file = os.path.join(root, filename)
                    output_file = os.path.join(output_dir, filename)
                    
                    try:
                        with open(input_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        acordaos = process_json_content(content)
                        if not acordaos:
                            continue
                            
                        if not isinstance(acordaos, list):
                            acordaos = [acordaos]
                        
                        processed_data = [process_acordao(acordao, index) for acordao in acordaos]
                        total_acordaos += len(processed_data)
                        
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(processed_data, f, ensure_ascii=False, indent=2)
                        
                        arquivos_processados += 1
                        
                        if arquivos_processados % 100 == 0:
                            print(f"Processados {arquivos_processados}/{total_arquivos} arquivos")
                            
                    except Exception as e:
                        erro = f"Erro ao processar {input_file}: {str(e)}"
                        print(erro)
                        erros.append(erro)
    
    fim = datetime.now()
    tempo_total = fim - inicio
    
    relatorio = f"""
=== Relatório de Processamento ===
Início: {inicio}
Fim: {fim}
Duração: {tempo_total}

Arquivos encontrados: {total_arquivos}
Arquivos processados: {arquivos_processados}
Total de acórdãos: {total_acordaos}
Erros: {len(erros)}

Erros detalhados:
{chr(10).join(erros)}
"""
    
    relatorio_path = os.path.join(output_base_path, "relatorio_processamento.txt")
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print(f"\nProcessamento concluído! Relatório salvo em: {relatorio_path}")

if __name__ == "__main__":
    input_path = r"D:\Dropbox\Github\Dados Abertos STJ\downloads"
    output_path = r"D:\Dropbox\Github\Dados Abertos STJ\Espelhos de Acordaos Parseados"
    
    print("Iniciando processamento...")
    process_directory(input_path, output_path)
    print("Processamento concluído!")