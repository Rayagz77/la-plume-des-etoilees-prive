FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps (Postgres libs for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Ensure Flask app factory is resolvable
ENV FLASK_APP=app:create_app
ENV PYTHONPATH=/app

EXPOSE 8000

# Entrypoint handles migrations then launches Gunicorn
CMD ["./docker/entrypoint.sh"]

RUN chmod +x docker/entrypoint.sh
RUN sed -i 's/\r$//' docker/entrypoint.sh
