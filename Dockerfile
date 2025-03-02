FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=app \
    SECRET_KEY="GOL"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -r appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 775 /app  # Permissões de leitura/escrita pro appuser

USER appuser

RUN [ -f flight_stats.db ] || touch flight_stats.db && \
    chmod 664 flight_stats.db

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:create_app()"]