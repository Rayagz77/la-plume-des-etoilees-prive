"""
Point d'entrée unique pour Mongo helpers.

On essaie d'importer les helpers réels.
Si PyMongo/APScheduler/connexion Mongo ne sont pas dispo,
on expose des stubs inoffensifs pour que l'app continue de démarrer.
"""

try:
    from .mongo import (
        get_mongo,
        log_login,
        log_action,
        close_mongo,
        init_mongo,
    )
except Exception as e:
    # Fallbacks silencieux : l'app fonctionne sans Mongo
    def init_mongo(app):
        try:
            app.logger.warning(f"Mongo/logging désactivé (raison: {e})")
        except Exception:
            pass
        return None

    def get_mongo():
        return None

    def log_login(*args, **kwargs):
        return False

    def log_action(*args, **kwargs):
        return False

    def close_mongo(*args, **kwargs):
        return None

__all__ = [
    "get_mongo",
    "log_login",
    "log_action",
    "close_mongo",
    "init_mongo",
]
