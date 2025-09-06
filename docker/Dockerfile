FROM python:3.12-slim

# OS deps utiles pour psycopg2 et build wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl wget git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installe d'abord les deps Python (cache Docker = builds plus rapides)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code
COPY . .

# Droits & utilisateur non-root
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app \
    && chmod +x docker/entrypoint.sh && sed -i 's/\r$//' docker/entrypoint.sh
USER appuser

EXPOSE 8000

ENTRYPOINT ["./docker/entrypoint.sh"]
