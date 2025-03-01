import pandas as pd
from sqlalchemy import create_engine
import os

def process_data(csv_path, chunksize=10000):
    """
    Processa o CSV em pedaços e salva no banco de dados.
    
    :param csv_path: Caminho do arquivo CSV
    :param chunksize: Tamanho do chunk, número de linhas por vez
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"O arquivo {csv_path} não foi encontrado.")
    
    engine = create_engine('sqlite:///flight_stats.db')
    chunk_iterator = pd.read_csv(
        csv_path, 
        encoding='utf-8', 
        delimiter=';', 
        chunksize=chunksize, 
        skiprows=1 
    )
    
    first_chunk = True
    for chunk in chunk_iterator:
        # Aplicar filtros com os nomes corretos das colunas
        chunk_filtered = chunk[
            (chunk['EMPRESA_SIGLA'] == 'GLO') &
            (chunk['GRUPO_DE_VOO'] == 'REGULAR') &
            (chunk['NATUREZA'] == 'DOMÉSTICA')
        ]
        
        # Criar a coluna MERCADO, tratando valores NaN
        chunk_filtered['MERCADO'] = chunk_filtered.apply(
            lambda row: ''.join(sorted([
                str(row['AEROPORTO_DE_ORIGEM_SIGLA']) if pd.notna(row['AEROPORTO_DE_ORIGEM_SIGLA']) else '',
                str(row['AEROPORTO_DE_DESTINO_SIGLA']) if pd.notna(row['AEROPORTO_DE_DESTINO_SIGLA']) else ''
            ])),
            axis=1
        )
        
        # Selecionar colunas relevantes
        chunk_final = chunk_filtered[['ANO', 'MES', 'MERCADO', 'RPK']]
        
        # Salvar no banco de dados
        if first_chunk:
            chunk_final.to_sql('flight_data', engine, if_exists='replace', index=False)
            first_chunk = False
        else:
            chunk_final.to_sql('flight_data', engine, if_exists='append', index=False)
        
        print(f"Processado chunk com {len(chunk_final)} linhas filtradas.")

if __name__ == "__main__":
    # Caminho do arquivo, caso de erro, coloque o caminho completo do arquivo.
    csv_path = r"C:\Users\lucas\OneDrive\Área de Trabalho\projetos\teste\data\Dados_Estatisticos.csv"
    process_data(csv_path)