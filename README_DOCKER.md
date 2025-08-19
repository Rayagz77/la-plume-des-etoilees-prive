# Démarrer l'app avec Docker

## 1) Variables d'environnement
Copiez le modèle et remplissez vos valeurs (ne commitez pas `.env`) :
```bash
cp .env.example .env
```

## 2) Lancer en local
```bash
docker compose up --build
# Ouvrir http://localhost:8000
```

## 3) Migrations (si utilisées)
Les migrations Alembic (Flask-Migrate) sont lancées automatiquement au démarrage (si le paquet est présent).

## 4) Notes
- `web` monte le dossier courant en volume: toute modif de code est prise en compte après un redémarrage.
- Postgres et Mongo persistent leurs données dans des volumes `pgdata` et `mongodata`.
- En production, retirez le volume `.:/app` et construisez une image immuable.
