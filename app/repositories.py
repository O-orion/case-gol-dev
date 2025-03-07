from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import pandas as pd
from .models import FilterData
from typing import List

class FlightDataRepository:
    """Repositório para acesso aos dados de voos no banco SQLite."""
    def __init__(self, db_path: str = 'postgresql+psycopg2://admin:1234@localhost:5432/flight_stats'):
        self.engine: Engine = create_engine(db_path)

    def get_all_flight_data(self) -> pd.DataFrame:
        """Recupera todos os dados de voos da tabela 'flight_data'."""
        return pd.read_sql('SELECT * FROM flight_data', self.engine)

    def get_filtered_flight_data(self, filter_data: FilterData) -> pd.DataFrame:
        """Recupera dados de voos filtrados por mercado e período."""
        query = """
            SELECT "ANO", "MES", "MERCADO", "RPK", "ASK" 
            FROM flight_data 
            WHERE "MERCADO" = %(mercado)s 
            AND (("ANO" > %(ano_inicio)s AND "ANO" < %(ano_fim)s) 
                 OR ("ANO" = %(ano_inicio)s AND "MES" >= %(mes_inicio)s) 
                 OR ("ANO" = %(ano_fim)s AND "MES" <= %(mes_fim)s))
        """
        return pd.read_sql(query, self.engine, params=filter_data.dict())

    def get_available_markets(self) -> List[str]:
        """Retorna a lista de mercados únicos disponíveis."""
        flight_data = self.get_all_flight_data()
        return sorted(flight_data['MERCADO'].unique().tolist())

    def get_available_years(self) -> List[int]:
        """Retorna a lista de anos únicos disponíveis."""
        flight_data = self.get_all_flight_data()
        return sorted(flight_data['ANO'].unique().tolist())