#!/usr/bin/env bash
set -euo pipefail

# Export Flask variables (in case .flaskenv isn't copied)
export FLASK_APP=${FLASK_APP:-app:create_app}
export FLASK_ENV=${FLASK_ENV:-production}

# Run DB migrations if Flask-Migrate is present and DB is reachable
if python -c "import importlib.util as u; import sys; sys.exit(0 if u.find_spec('flask_migrate') else 1)"; then
  echo "Running Alembic migrations (flask db upgrade)..."
  # Give DB a moment to accept connections (compose depends_on doesn't wait for readiness)
  python - <<'PY'
import os, time
import socket

host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))

for i in range(30):
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except OSError:
        time.sleep(1)
PY
  flask db upgrade || echo "⚠️  Migrations skipped (no Flask app context or DB not ready)."
fi

# Launch Gunicorn with the factory pattern
exec gunicorn -b 0.0.0.0:8000 "app:create_app()"
