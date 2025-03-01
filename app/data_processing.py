import pandas as pd
from sqlalchemy import create_engine
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    total_rows = 0
    
    for i, chunk in enumerate(chunk_iterator):
        logger.info(f"Processando chunk {i + 1} com {len(chunk)} linhas totais")
        
        # Verificar colunas disponíveis
        logger.info(f"Colunas no chunk: {chunk.columns.tolist()}")
        
        # Aplicar filtros
        chunk_filtered = chunk[
            (chunk['EMPRESA_SIGLA'] == 'GLO') &
            (chunk['GRUPO_DE_VOO'] == 'REGULAR') &
            (chunk['NATUREZA'] == 'DOMÉSTICA')
        ]
        
        logger.info(f"Linhas após filtro: {len(chunk_filtered)}")
        
        # Criar a coluna MERCADO
        chunk_filtered['MERCADO'] = chunk_filtered.apply(
            lambda row: ''.join(sorted([
                str(row['AEROPORTO_DE_ORIGEM_SIGLA']) if pd.notna(row['AEROPORTO_DE_ORIGEM_SIGLA']) else '',
                str(row['AEROPORTO_DE_DESTINO_SIGLA']) if pd.notna(row['AEROPORTO_DE_DESTINO_SIGLA']) else ''
            ])),
            axis=1
        )
        
        # Selecionar colunas relevantes
        chunk_final = chunk_filtered[['ANO', 'MES', 'MERCADO', 'RPK']]
        total_rows += len(chunk_final)
        
        # Salvar no banco de dados
        if first_chunk:
            chunk_final.to_sql('flight_data', engine, if_exists='replace', index=False)
            logger.info(f"Tabela criada com {len(chunk_final)} linhas no primeiro chunk")
            first_chunk = False
        else:
            chunk_final.to_sql('flight_data', engine, if_exists='append', index=False)
            logger.info(f"Adicionado {len(chunk_final)} linhas ao banco")
        
    if total_rows == 0:
        logger.warning("Nenhum dado foi inserido no banco. Verifique os filtros ou o CSV.")

if __name__ == "__main__":
    csv_path = r"C:\Users\lucas\OneDrive\Área de Trabalho\projetos\teste\data\Dados_Estatisticos.csv"
    process_data(csv_path)