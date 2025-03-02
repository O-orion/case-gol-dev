# tests/test_services.py
import pytest
import pandas as pd
from app.services import get_flight_data, get_flight_data_csv, get_dashboard_initial_data, FilterData
from app.repositories import FlightDataRepository
from pytest_mock import MockerFixture

@pytest.fixture
def mock_repo(mocker: MockerFixture) -> FlightDataRepository:
    """Cria um mock do FlightDataRepository."""
    mock = mocker.patch('app.repositories.FlightDataRepository', autospec=True)
    mock_instance = mock.return_value
    mock_instance.get_all_flight_data.return_value = pd.DataFrame({
        'ANO': [2023, 2023, 2024],
        'MES': [1, 2, 1],
        'MERCADO': ['SBGRSBSV', 'SBGRSBSV', 'SBFLSBGR'],
        'RPK': [1000, 2000, 1500]
    })
    mock_instance.get_filtered_flight_data.return_value = pd.DataFrame({
        'ANO': [2023, 2023],
        'MES': [1, 2],
        'MERCADO': ['SBGRSBSV', 'SBGRSBSV'],
        'RPK': [1000, 2000]
    })
    mock_instance.get_available_markets.return_value = ['SBFLSBGR', 'SBGRSBSV']
    mock_instance.get_available_years.return_value = [2023, 2024]
    return mock_instance

def test_get_dashboard_initial_data(mock_repo):
    """Testa se get_dashboard_initial_data retorna mercados e anos corretamente."""
    initial_data = get_dashboard_initial_data(mock_repo)
    assert initial_data == {
        'mercados': ['SBFLSBGR', 'SBGRSBSV'],
        'anos': [2023, 2024]
    }

def test_get_flight_data_success(mock_repo):
    """Testa get_flight_data com dados válidos."""
    filter_data = FilterData(
        mercado='SBGRSBSV',
        ano_inicio=2023,
        ano_fim=2023,
        mes_inicio=1,
        mes_fim=2
    )
    chart_data = get_flight_data(filter_data, mock_repo)
    assert chart_data == {
        'labels': ['2023-01', '2023-02'],
        'values': [1000, 2000],
        'single_point': False,
        'message': None
    }

def test_get_flight_data_no_data(mock_repo, mocker):
    """Testa get_flight_data quando não há dados."""
    mocker.patch.object(mock_repo, 'get_filtered_flight_data', return_value=pd.DataFrame())
    filter_data = FilterData(
        mercado='SBGRSBSV',
        ano_inicio=2025,
        ano_fim=2025
    )
    chart_data = get_flight_data(filter_data, mock_repo)
    assert 'labels' in chart_data and chart_data['labels'] == []
    assert 'message' in chart_data and 'Nenhum dado encontrado' in chart_data['message']

def test_get_flight_data_csv(mock_repo):
    """Testa get_flight_data_csv com dados válidos."""
    filter_data = FilterData(
        mercado='SBGRSBSV',
        ano_inicio=2023,
        ano_fim=2023
    )
    csv_content = get_flight_data_csv(filter_data, mock_repo)
    # Normaliza os finais de linha pra \n
    csv_content = csv_content.replace('\r\n', '\n')
    expected = "ANO,MES,MERCADO,RPK\n2023,1,SBGRSBSV,1000\n2023,2,SBGRSBSV,2000\n"
    assert csv_content == expected