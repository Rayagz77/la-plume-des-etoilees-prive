"""
Point d'entrée unique pour Mongo helpers :

    from extensions import log_login, log_action, get_mongo, init_mongo
"""

from .mongo import (
    get_mongo,
    log_login,
    log_action,
    close_mongo,
    init_mongo,      # ⭐️ on l’importe ET on l’exporte
)

__all__ = [
    "get_mongo",
    "log_login",
    "log_action",
    "close_mongo",
    "init_mongo",    # ⭐️ ajouté
]
