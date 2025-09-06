from __future__ import annotations

from pathlib import Path
import os, sys
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

# Mail optionnel
try:
    from flask_mail import Mail
    MAIL_ENABLED = True
except Exception:
    Mail = None  # type: ignore
    MAIL_ENABLED = False

# Stripe optionnel
try:
    import stripe
except Exception:
    stripe = None  # type: ignore

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# --- Env ---
# Local : .env ; Docker : env_file dans docker-compose
load_dotenv(BASE_DIR / ".env", override=True)

# ---------- DB URI ----------
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))
DB_HOST = os.getenv("DB_HOST", "db")  # "db" en Docker ; mets "localhost" dans .env si besoin
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "db_psql_library")

DEFAULT_DB_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URI = (
    os.getenv("SQLALCHEMY_DATABASE_URI")  # ex: sqlite:///instance/app.db en local
    or os.getenv("DATABASE_URI")
    or DEFAULT_DB_URI
)

# ---------- Modules du projet ----------
from models import db  # noqa: E402
from models.book_model import Book  # noqa: E402
from models.user_model import User  # noqa: E402
from models.category_model import Category  # noqa: E402
from models.cart_items_model import CartItem  # noqa: E402

from controllers.register_controller import register_bp  # noqa: E402
from controllers.auth_controller import login_bp  # noqa: E402
from controllers.admin_controller import admin_bp  # noqa: E402
from controllers.cart_controller import cart_bp  # noqa: E402
from controllers.payement_controller import payement_bp  # noqa: E402
from controllers.account_controller import account_bp  # noqa: E402


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config.update(
        SQLALCHEMY_DATABASE_URI=DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-change-me"),
        TEMPLATES_AUTO_RELOAD=True,
    )

    # --- Extensions
    db.init_app(app)
    Migrate(app, db)

    # Mongo optionnel (import ici pour éviter les ImportError si extension absente)
    try:
        if os.getenv("MONGODB_URI"):
            from extensions import init_mongo  # type: ignore
            init_mongo(app)
        else:
            app.logger.info("Mongo désactivé (MONGODB_URI manquant).")
    except Exception as e:
        app.logger.warning(f"Mongo désactivé: {e}")

    # Mail optionnel
    if MAIL_ENABLED:
        mail = Mail()
        app.config.update(
            MAIL_SERVER=os.getenv("MAIL_SERVER", "localhost"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", "25")),
            MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "false").lower() == "true",
            MAIL_USE_SSL=os.getenv("MAIL_USE_SSL", "false").lower() == "true",
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
            MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", "no-reply@example.com"),
        )
        mail.init_app(app)
    else:
        app.logger.warning("Flask-Mail non installé → fonctions e-mail désactivées.")

    # Stripe optionnel (clé secrète serveur)
    if stripe:
        key = os.getenv("STRIPE_SECRET_KEY")
        if key:
            stripe.api_key = key
        else:
            app.logger.info("STRIPE_SECRET_KEY manquant → Stripe désactivé.")

    # ---- Auth
    login_mgr = LoginManager(app)
    login_mgr.login_view = "login_bp.login"
    login_mgr.login_message_category = "warning"

    @login_mgr.user_loader
    def load_user(user_id: str):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # ---- Blueprints applicatifs
    app.register_blueprint(register_bp, url_prefix="/register")
    app.register_blueprint(login_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp)   # sans url_prefix
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(payement_bp, url_prefix="/payement")
    app.register_blueprint(account_bp, url_prefix="/account")

    # Webhook Stripe (controllers/stripe_hooks.py)
    try:
        from controllers.stripe_hooks import bp as stripe_hooks_bp  # type: ignore
        app.register_blueprint(stripe_hooks_bp)
    except Exception as e:
        app.logger.info(f"Stripe webhook non chargé: {e}")

    # ---- Contexte templates (panier)
    @app.context_processor
    def inject_cart_data():
        user_id = current_user.id if getattr(current_user, "is_authenticated", False) else session.get("user_id")
        if user_id:
            try:
                cart_items = CartItem.query.filter_by(user_id=user_id).all()
                total_price = sum((item.book.book_price or 0) for item in cart_items)
                return dict(
                    cart_items=cart_items,
                    total_price=total_price,
                    cart_count=len(cart_items),
                )
            except Exception as e:
                app.logger.warning(f"inject_cart_data error: {e}")
        return dict(cart_items=[], total_price=0, cart_count=0)

    # ---- Routes publiques
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/books")
    def gallery():
        selected_category_id = request.args.get("category", type=int)
        page = request.args.get("page", 1, type=int)
        per_page = 9

        query = Book.query
        if selected_category_id:
            query = query.filter_by(category_id=selected_category_id)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return render_template(
            "gallery.html",
            books=pagination.items,
            pagination=pagination,
            categories=Category.query.all(),
            selected_category_id=selected_category_id,
        )

    @app.route("/books/<int:book_id>")
    def book_detail(book_id: int):
        book = Book.query.get_or_404(book_id)
        return render_template("book_detail.html", book=book)

    return app


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    create_app().run(debug=debug)
