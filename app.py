from __future__ import annotations

"""Flask application factory (robust version).

– Charge .env une seule fois.
– Construit l’URI PostgreSQL en échappant correctement le mot de passe.
– Rend Stripe et Mongo optionnels en dev.
– Ajoute la config Mail (Mailpit en dev).
"""

from pathlib import Path
import os
import sys
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import stripe

# ----------------------------------------------------------------------------
#  Environnement & variables
# ----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# S'assure que le dossier projet est dans PYTHONPATH pour que ``import models`` fonctionne
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

load_dotenv(BASE_DIR / ".env", override=True)  # charge .env (UTF-8 conseillé)

print(f"⇢ Python interpreter : {sys.executable}")
print(f"⇢ .env loaded from  : {BASE_DIR / '.env'}")

# -- Construction sûre de l'URI Postgres
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASSWORD: str = quote_plus(os.getenv("DB_PASSWORD", ""))
# En Docker, l'hôte par défaut est le service compose "db"
DB_HOST: str = os.getenv("DB_HOST", "db")
DB_PORT: str = os.getenv("DB_PORT", "5432")
# ⚠️ Aligné sur ta base actuelle (db_psql_labrary)
DB_NAME: str = os.getenv("DB_NAME", "db_psql_labrary")

DEFAULT_DB_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Priorité à SQLALCHEMY_DATABASE_URI, puis DATABASE_URI, sinon fallback
DATABASE_URI = (
    os.getenv("SQLALCHEMY_DATABASE_URI")
    or os.getenv("DATABASE_URI")
    or DEFAULT_DB_URI
)

# ----------------------------------------------------------------------------
#  Imports des modèles / blueprints / extensions
# ----------------------------------------------------------------------------
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

from extensions import init_mongo  # noqa: E402

# Stripe : optionnel (ne pas faire planter si clé absente en dev)
stripe_key = os.getenv("STRIPE_SECRET_KEY")
if stripe_key:
    stripe.api_key = stripe_key
else:
    print("⚠️  STRIPE_SECRET_KEY manquant → Stripe désactivé dans cet environnement.")

# ----------------------------------------------------------------------------
#  Flask factory
# ----------------------------------------------------------------------------
def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ---- Core configuration
    app.config.update(
        SQLALCHEMY_DATABASE_URI=DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.getenv("SECRET_KEY"),
    )

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY is missing from environment")

    print("⇢ SQLAlchemy URI :", app.config["SQLALCHEMY_DATABASE_URI"])

    # ---- Extensions
    db.init_app(app)
    Migrate(app, db)

    # Mongo optionnel (ne pas casser si non configuré)
    try:
        if os.getenv("MONGODB_URI"):
            init_mongo(app)
        else:
            app.logger.info("Mongo désactivé (MONGODB_URI manquant).")
    except Exception as e:
        app.logger.warning(f"Mongo désactivé: {e}")

    # Mail (Mailpit en dev, SMTP en prod)
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

    # ---- Authentication
    login_mgr = LoginManager(app)
    login_mgr.login_view = "login_bp.login"
    login_mgr.login_message_category = "warning"

    @login_mgr.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # ---- Blueprints applicatifs
    app.register_blueprint(register_bp, url_prefix="/register")
    app.register_blueprint(login_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(payement_bp, url_prefix="/payement")
    app.register_blueprint(account_bp, url_prefix="/account")

    # (Optionnel) Webhook Stripe si présent
    try:
        from controllers.stripe_hooks import bp as stripe_hooks_bp  # type: ignore
        app.register_blueprint(stripe_hooks_bp)
    except Exception as e:
        app.logger.info(f"Stripe webhook non chargé: {e}")

    # ---- Template context processors
    @app.context_processor
    def inject_cart_data():
        if "user_id" in session:
            cart_items = CartItem.query.filter_by(user_id=session["user_id"]).all()
            total_price = sum(item.book.book_price for item in cart_items)
            return dict(
                cart_items=cart_items,
                total_price=total_price,
                cart_count=len(cart_items),
            )
        return dict(cart_items=[], total_price=0, cart_count=0)

    # ---- Routes
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


# ----------------------------------------------------------------------------
#  Entrée directe
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    create_app().run(debug=True)
