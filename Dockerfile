FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=app \
    SECRET_KEY="GOL"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

RUN useradd -m -r appuser && chown appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:create_app()"]