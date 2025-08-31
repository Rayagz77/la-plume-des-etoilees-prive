#!/usr/bin/env bash
set -euo pipefail

# 1) Dire à la CLI comment créer l'app Flask
export FLASK_APP="app:create_app"

# (optionnel) Mode debug/logs plus verbeux en dev
export FLASK_ENV=production
export FLASK_DEBUG=0

echo "Running Alembic migrations..."
# 2) Migrations : ont besoin de l'app (donc de FLASK_APP)
flask db upgrade || echo "⚠️  Migrations skipped (no Flask app context or DB not ready)."

# 3) Lancer le serveur WSGI
exec gunicorn -w 2 -b 0.0.0.0:8000 "app:create_app()"
