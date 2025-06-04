from datetime import datetime, timedelta
from typing import Optional, Dict, Any, TYPE_CHECKING
import os

from flask import current_app, request
from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_RUNNING


class MongoLogger:
    """
    Gestion centralisée de MongoDB :
      • connexion unique (singleton)
      • purge automatique des logs
      • indexation
    """

    _instance: "MongoLogger | None" = None
    _scheduler: BackgroundScheduler | None = None

    # ------------------------------------------------------------------ #
    # Singleton
    # ------------------------------------------------------------------ #
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_connection()
            cls._instance._init_scheduler()
        return cls._instance

    # ------------------------------------------------------------------ #
    # Initialisation
    # ------------------------------------------------------------------ #
    def _init_connection(self):
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise ValueError("⚠️  MONGODB_URI manquant dans l'environnement")

        try:
            self.client = MongoClient(
                uri,
                connectTimeoutMS=3_000,
                socketTimeoutMS=5_000,
                serverSelectionTimeoutMS=5_000,
            )
            self.db = self.client[os.getenv("MONGODB_DB", "library_analytics")]
            self._ensure_indexes()
        except PyMongoError as e:
            print(f"[MongoLogger] Connexion impossible → {e}")
            raise

    def _init_scheduler(self):
        if self._scheduler is None:
            self._scheduler = BackgroundScheduler()
            self._scheduler.add_job(
                self.purge_old_data,
                trigger="cron",
                day="*",
                hour=3,
                timezone="UTC",
                id="purge_old_logs",
            )
            self._scheduler.start()

    def _ensure_indexes(self):
        self.db.users_loggings.create_index(
            [("user_id", DESCENDING), ("timestamp", DESCENDING)]
        )
        self.db.user_actions.create_index(
            [("event_type", DESCENDING), ("timestamp", DESCENDING)]
        )
        # TTL 100 j (sécurité si la purge Python échoue)
        self.db.users_loggings.create_index("timestamp", expireAfterSeconds=100 * 86400)
        self.db.user_actions.create_index("timestamp", expireAfterSeconds=100 * 86400)

    # ------------------------------------------------------------------ #
    # API
    # ------------------------------------------------------------------ #
    def log_event(
        self,
        collection: str,
        user_id: Optional[int],
        email: str,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        try:
            doc = {
                "user_id": user_id,
                "email": self._sanitize_email(email),
                "event_type": event_type,
                "timestamp": datetime.utcnow(),
                "http_metadata": {
                    "ip": self._get_client_ip(),
                    "method": request.method,
                    "path": request.path,
                    "user_agent": self._sanitize_user_agent(request.user_agent.string),
                },
            }
            if metadata:
                doc["details"] = metadata
            self.db[collection].insert_one(doc)
            return True
        except PyMongoError as e:
            current_app.logger.warning(f"[MongoLogger] Échec log_event : {e}")
            return False

    def purge_old_data(self, retention_days: int = 90):
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        try:
            r1 = self.db.users_loggings.delete_many({"timestamp": {"$lt": cutoff}})
            r2 = self.db.user_actions.delete_many({"timestamp": {"$lt": cutoff}})
            current_app.logger.info(
                f"Purge auto : {r1.deleted_count} logins + {r2.deleted_count} actions."
            )
        except PyMongoError as e:
            current_app.logger.error(f"[MongoLogger] Purge KO : {e}")

    # ------------------------------------------------------------------ #
    # Helpers internes
    # ------------------------------------------------------------------ #
    @staticmethod
    def _sanitize_email(email: str) -> str:
        return email.strip()[:100]

    @staticmethod
    def _sanitize_user_agent(ua: str) -> str:
        return ua[:200] if ua else "unknown"

    @staticmethod
    def _get_client_ip() -> str:
        return request.headers.get("X-Forwarded-For", request.remote_addr)

    # ------------------------------------------------------------------ #
    # Fermeture
    # ------------------------------------------------------------------ #
    def close(self):
        if hasattr(self, "client"):
            self.client.close()
        if (
            self._scheduler
            and self._scheduler.state == STATE_RUNNING
        ):
            try:
                self._scheduler.shutdown()
            except Exception as e:
                current_app.logger.warning(f"[MongoLogger] shutdown fail: {e}")


# ---------------------------------------------------------------------- #
#  Intégration Flask
# ---------------------------------------------------------------------- #
def init_mongo(app):
    """À appeler depuis app.py (ou la factory) après avoir créé *app*."""
    logger = MongoLogger()
    app.extensions["mongo_logger"] = logger

    @app.teardown_appcontext
    def _shutdown_mongo(exc=None):
        logger.close()


# ---------------------------------------------------------------------- #
#  Wrappers fonctionnels (compatibilité ascendante)
# ---------------------------------------------------------------------- #
if TYPE_CHECKING:
    from flask import Flask


def _logger() -> MongoLogger:
    return current_app.extensions["mongo_logger"]  # type: ignore


def get_mongo() -> MongoLogger:  # ancien helper direct
    return _logger()


def log_login(
    user_id: Optional[int],
    email: str,
    role: Optional[str],
    status: str,
    ip_addr: str,
) -> bool:
    meta = {"status": status, "role": role, "ip": ip_addr}
    return _logger().log_event("users_loggings", user_id, email, "login", meta)


def log_action(
    user_id: int,
    email: str,
    role: str,
    action_type: str,
    **extra,
) -> bool:
    meta = {"role": role, **extra}
    return _logger().log_event("user_actions", user_id, email, action_type, meta)


def close_mongo(exc: Exception | None = None):
    """Wrapper compatible Flask pour la fermeture."""
    _logger().close()
