from typing import List, Dict, Union
from flask import flash
import pandas as pd
import logging
import io 
from .models import FilterData
from .repositories import FlightDataRepository
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

logger = logging.getLogger(__name__)

def get_dashboard_initial_data(repo: FlightDataRepository) -> Dict[str, List]:
    """Recupera os mercados e anos disponíveis para o dashboard."""
    return {
        'mercados': repo.get_available_markets(),
        'anos': repo.get_available_years()
    }

def get_flight_data(filter_data: FilterData, repo: FlightDataRepository) -> Dict[str, Union[List, str]]:
    """
    Recupera dados filtrados do banco e retorna no formato para o gráfico.

    Args:
        filter_data: Filtros de mercado e período.
        repo: Repositório para acesso aos dados de voos.

    Returns:
        Dicionário com labels, valores, mensagem e indicador de ponto único.

    Raises:
        ValueError: Se o mercado não existir nos dados.
    """
    logger.info(f"Filtros aplicados: {filter_data.dict()}")

    flight_data: pd.DataFrame = repo.get_filtered_flight_data(filter_data)
    available_markets: List[str] = repo.get_available_markets()
    if filter_data.mercado not in available_markets:
        logger.warning(f"Mercado inválido: {filter_data.mercado}")
        raise ValueError("Mercado selecionado não existe.")

    logger.info(f"Dados filtrados: {len(flight_data)} linhas encontradas")

    if flight_data.empty:
        full_data = repo.get_all_flight_data()
        available_years = full_data[full_data['MERCADO'] == filter_data.mercado]['ANO'].unique().tolist()
        available_months = full_data[full_data['MERCADO'] == filter_data.mercado]['MES'].unique().tolist()
        logger.info(f"Dados disponíveis para {filter_data.mercado} - Anos: {available_years}, Meses: {available_months}")
        return {
            'labels': [],
            'values': [],
            'message': f"Nenhum dado encontrado para {filter_data.mercado} entre {filter_data.ano_inicio}-{filter_data.mes_inicio} e {filter_data.ano_fim}-{filter_data.mes_fim}.",
            'single_point': False
        }

    flight_data['RPK'] = pd.to_numeric(flight_data['RPK'], errors='coerce').fillna(0)
    logger.info("OLÁA")
    labels: List[str] = (
        flight_data['ANO'].astype(str) + '-' + 
        flight_data['MES'].astype(str).str.zfill(2)
    ).tolist()
    values: List[float] = flight_data['RPK'].tolist()

    logger.info(f"Labels gerados: {labels[:5]}... (total: {len(labels)})")

    return {
        'labels': labels,
        'values': values,
        'single_point': len(labels) == 1,
        'message': None
    }

def get_flight_data_csv(filter_data: FilterData, repo: FlightDataRepository) -> str:
    """Gera uma string CSV com os dados filtrados para exportação."""
    flight_data: pd.DataFrame = repo.get_filtered_flight_data(filter_data)

    if flight_data.empty:
        logger.info("Nenhum dado para exportar em CSV")
        return "ANO,MES,MERCADO,RPK\n"

    flight_data['RPK'] = pd.to_numeric(flight_data['RPK'], errors='coerce').fillna(0)
    csv_content: str = flight_data[['ANO', 'MES', 'MERCADO', 'RPK']].to_csv(index=False)
    logger.info(f"Gerado CSV com {len(flight_data)} linhas")
    return csv_content

def get_flight_data_pdf(filter_data: FilterData, repo: FlightDataRepository) -> io.BytesIO:
    """
    Gera um PDF com os dados filtrados do dashboard.

    Args:
        filter_data: Filtros de mercado e período.
        repo: Repositório para acesso aos dados de voos.

    Returns:
        Buffer de bytes contendo o PDF gerado, ou None se não houver dados ou erro.
    """
    logger.info(f"Gerando PDF para filtros: {filter_data.model_dump()}")
    flight_data: pd.DataFrame = repo.get_filtered_flight_data(filter_data)
    
    if flight_data.empty:
        logger.info("Nenhum dado para exportar em PDF")
        flash("Nenhum dado encontrado para os filtros selecionados.", "warning")  # Adiciona flash aqui pra debug
        return None

    logger.info(f"Dados para PDF (primeiras 5 linhas): {flight_data.head().to_dict(orient='records')}")
    flight_data['RPK'] = pd.to_numeric(flight_data['RPK'], errors='coerce').fillna(0)
    
    # Prepara os dados pra tabela no PDF
    data = [flight_data.columns.tolist()] + flight_data.values.tolist()
    logger.info(f"Dados preparados para tabela (primeiras 2 linhas): {data[:2]}")
    
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        table = Table(data)
        
        # Estiliza a tabela
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        doc.build([table])
        buffer.seek(0)
        logger.info(f"PDF gerado com {len(flight_data)} linhas, tamanho do buffer: {buffer.getbuffer().nbytes} bytes")
        
        # Verifica se o buffer tem conteúdo
        if buffer.getbuffer().nbytes == 0:
            logger.error("Buffer do PDF está vazio após geração")
            return None
        
        # Salva o buffer em um arquivo temporário pra debug
        with open("debug_output.pdf", "wb") as f:
            f.write(buffer.getvalue())
        logger.info("PDF salvo em 'debug_output.pdf' para inspeção")
        
        return buffer
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}", exc_info=True)
        return None
    

def get_flight_RPK(filter_data: FilterData, repo: FlightDataRepository) -> Dict[str, Union[List, str]]:

    logger.info(f"Filtros aplicados: {filter_data.dict()}")

    flight_data: pd.DataFrame = repo.get_filtered_flight_data(filter_data)
    available_markets: List[str] = repo.get_available_markets()
    if filter_data.mercado not in available_markets:
        logger.warning(f"Mercado inválido: {filter_data.mercado}")
        raise ValueError("Mercado selecionado não existe.")

    logger.info(f"Dados filtrados: {len(flight_data)} linhas encontradas")

    if flight_data.empty:
        full_data = repo.get_all_flight_data()
        available_years = full_data[full_data['MERCADO'] == filter_data.mercado]['ANO'].unique().tolist()
        available_months = full_data[full_data['MERCADO'] == filter_data.mercado]['MES'].unique().tolist()
        logger.info(f"Dados disponíveis para {filter_data.mercado} - Anos: {available_years}, Meses: {available_months}")
        return {
            'labels': [],
            'values': [],
            'message': f"Nenhum dado encontrado para {filter_data.mercado} entre {filter_data.ano_inicio}-{filter_data.mes_inicio} e {filter_data.ano_fim}-{filter_data.mes_fim}.",
            'single_point': False
        }

    flight_data['RPK'] = pd.to_numeric(flight_data['RPK'], errors='coerce').fillna(0) 
    

    logger.info("")
    logger.info(flight_data['ASK'])
    logger.info("")

    flight_data['RPK'] = flight_data['RPK'] / flight_data['ASK']

    labels: List[str] = (
        flight_data['ANO'].astype(str) + '-' + 
        flight_data['MES'].astype(str).str.zfill(2)
    ).tolist()
    values: List[float] = flight_data['RPK'].tolist()

    logger.info(f"Labels gerados: {labels[:5]}... (total: {len(labels)})")

    return {
        'labels': labels,
        'values': values,
        'single_point': len(labels) == 1,
        'message': None
    }
