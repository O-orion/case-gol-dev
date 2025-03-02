import pytest
import pandas as pd
from sqlalchemy import create_engine
from app.repositories import FlightDataRepository
from app.models import FilterData

@pytest.fixture
def in_memory_db():
    """Cria um banco SQLite em memória para testes."""
    engine = create_engine('sqlite:///:memory:')
    df = pd.DataFrame({
        'ANO': [2023, 2023, 2024],
        'MES': [1, 2, 1],
        'MERCADO': ['SBGRSBSV', 'SBGRSBSV', 'SBFLSBGR'],
        'RPK': [1000, 2000, 1500]
    })
    df.to_sql('flight_data', engine, if_exists='replace', index=False)
    return engine

@pytest.fixture
def repo(in_memory_db):
    """Cria uma instância do FlightDataRepository com o banco em memória configurado."""
    repo = FlightDataRepository()
    repo.engine = in_memory_db
    return repo

def test_get_all_flight_data(repo):
    """Testa se get_all_flight_data retorna todos os dados corretamente."""
    flight_data = repo.get_all_flight_data()
    assert len(flight_data) == 3
    assert list(flight_data.columns) == ['ANO', 'MES', 'MERCADO', 'RPK']
    assert flight_data['MERCADO'].tolist() == ['SBGRSBSV', 'SBGRSBSV', 'SBFLSBGR']

def test_get_filtered_flight_data(repo):
    """Testa se get_filtered_flight_data filtra os dados corretamente."""
    filter_data = FilterData(
        mercado='SBGRSBSV',
        ano_inicio=2023,
        ano_fim=2023,
        mes_inicio=1,
        mes_fim=2
    )
    filtered_data = repo.get_filtered_flight_data(filter_data)
    assert len(filtered_data) == 2
    assert filtered_data['MERCADO'].tolist() == ['SBGRSBSV', 'SBGRSBSV']
    assert filtered_data['ANO'].tolist() == [2023, 2023]
    assert filtered_data['MES'].tolist() == [1, 2]

def test_get_available_markets(repo):
    """Testa se get_available_markets retorna mercados únicos ordenados."""
    markets = repo.get_available_markets()
    assert markets == ['SBFLSBGR', 'SBGRSBSV']

def test_get_available_years(repo):
    """Testa se get_available_years retorna anos únicos ordenados."""
    years = repo.get_available_years()
    assert years == [2023, 2024]