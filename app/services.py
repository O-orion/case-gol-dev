from sqlalchemy import create_engine
import pandas as pd
from pydantic import BaseModel, validator
from typing import List, Dict, Union
import logging

logger = logging.getLogger(__name__)

class FilterData(BaseModel):
    mercado: str
    ano_inicio: int
    ano_fim: int
    mes_inicio: int = 1
    mes_fim: int = 12

    @validator('ano_fim')
    def ano_fim_maior_que_inicio(cls, v, values):
        if 'ano_inicio' in values and v < values['ano_inicio']:
            raise ValueError('Ano fim deve ser maior ou igual ao ano início.')
        return v

    @validator('mes_fim')
    def mes_fim_valido(cls, v, values):
        if 'mes_inicio' in values and 'ano_inicio' in values and 'ano_fim' in values:
            if values['ano_inicio'] == values['ano_fim'] and v < values['mes_inicio']:
                raise ValueError('Mês fim deve ser maior ou igual ao mês início no mesmo ano.')
        return v

def get_dashboard_initial_data(db_path: str = 'flight_stats.db') -> Dict[str, List]:
    """Recupera os mercados e anos disponíveis para o dashboard."""
    engine = create_engine(f'sqlite:///{db_path}')
    df = pd.read_sql('SELECT * FROM flight_data', con=engine)
    return {
        'mercados': sorted(df['MERCADO'].unique().tolist()),
        'anos': sorted(df['ANO'].unique().tolist())
    }

def get_flight_data(filter_data: FilterData, db_path: str = 'flight_stats.db') -> Dict[str, Union[List, str]]:
    """Recupera dados filtrados do banco e retorna no formato para o gráfico."""
    engine = create_engine(f'sqlite:///{db_path}')
    df = pd.read_sql('SELECT * FROM flight_data', con=engine)

    logger.info(f"Filtros aplicados: {filter_data.dict()}")

    mercados = df['MERCADO'].unique().tolist()
    if filter_data.mercado not in mercados:
        logger.warning(f"Mercado inválido: {filter_data.mercado}")
        raise ValueError("Mercado selecionado não existe.")

    # Filtragem ajustada para considerar ano e mês juntos
    data = df[
        (df['MERCADO'] == filter_data.mercado) &
        (
            ((df['ANO'] > filter_data.ano_inicio) & (df['ANO'] < filter_data.ano_fim)) |
            ((df['ANO'] == filter_data.ano_inicio) & (df['MES'] >= filter_data.mes_inicio)) |
            ((df['ANO'] == filter_data.ano_fim) & (df['MES'] <= filter_data.mes_fim))
        )
    ]

    logger.info(f"Dados filtrados: {len(data)} linhas encontradas")

    if data.empty:
        available_years = df[df['MERCADO'] == filter_data.mercado]['ANO'].unique().tolist()
        available_months = df[df['MERCADO'] == filter_data.mercado]['MES'].unique().tolist()
        logger.info(f"Dados disponíveis para {filter_data.mercado} - Anos: {available_years}, Meses: {available_months}")
        return {
            'labels': [],
            'values': [],
            'message': f"Nenhum dado encontrado para {filter_data.mercado} entre {filter_data.ano_inicio}-{filter_data.mes_inicio} e {filter_data.ano_fim}-{filter_data.mes_fim}.",
            'single_point': False
        }

    data['RPK'] = pd.to_numeric(data['RPK'], errors='coerce').fillna(0)
    labels = (data['ANO'].astype(str) + '-' + data['MES'].astype(str).str.zfill(2)).tolist()
    values = data['RPK'].tolist()

    logger.info(f"Labels gerados: {labels[:5]}... (total: {len(labels)})")

    return {
        'labels': labels,
        'values': values,
        'single_point': len(labels) == 1,
        'message': None
    }