import os
import sys
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from flask_migrate import Migrate
import stripe


# 📌 Ajouter le répertoire courant au PYTHONPATH pour faciliter les imports internes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 📌 Charger les variables d'environnement
load_dotenv()

# 📌 Importer les modules internes
from models import db  # Vérifier que models/__init__.py expose bien "db"
from models.book_model import Book
from models.category_model import Category
from models.author_model import Author
from models.cart_items_model import CartItem
from controllers.register_controller import register_bp
from controllers.auth_controller import login_bp
from controllers.admin_controller import admin_bp
from controllers.cart_controller import cart_bp
from controllers.payement_controller import payement_bp
from controllers.account_controller import account_bp


# 📌 Configuration de Stripe (obligatoire pour le paiement)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY doit être défini dans le fichier .env")

def create_app():
    """Créer et configurer l'application Flask."""
    app = Flask(__name__)

    # 📌 Configuration de la base de données
    db_uri = os.getenv("DATABASE_URI")
    secret_key = os.getenv("SECRET_KEY")

    if not db_uri:
        raise ValueError("Erreur : DATABASE_URI doit être défini dans .env")
    if not secret_key:
        raise ValueError("Erreur : SECRET_KEY doit être défini dans .env")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = secret_key

    # 📌 Initialisation de SQLAlchemy et Flask-Migrate
    db.init_app(app)  
    migrate = Migrate(app, db)

    # 📌 Enregistrement des blueprints
    app.register_blueprint(register_bp, url_prefix='/register')
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(payement_bp, url_prefix='/payement')
    app.register_blueprint(account_bp, url_prefix='/account')

    # 📌 Contexte global : Nombre d'articles dans le panier
    @app.context_processor
    def inject_cart_count():
        user_id = session.get('user_id')
        cart_count = CartItem.query.filter_by(user_id=user_id).count() if user_id else 0
        return {'cart_count': cart_count}

    # 📌 Route principale : page d'accueil
    @app.route('/')
    def home():
        return render_template('home.html')

    # 📌 Route pour la galerie de livres (avec pagination et filtres)
    @app.route('/books')
    def gallery():
        try:
            selected_category_id = request.args.get('category', type=int)
            page = request.args.get('page', 1, type=int)
            per_page = 9  # Nombre de livres affichés par page

            if selected_category_id:
                pagination = Book.query.filter_by(category_id=selected_category_id)\
                                    .paginate(page=page, per_page=per_page, error_out=False)
            else:
                pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)

            return render_template('gallery.html',
                                   books=pagination.items,
                                   pagination=pagination,
                                   categories=Category.query.all(),
                                   selected_category_id=selected_category_id)
        except Exception as e:
            print(f"⚠️ Erreur dans gallery(): {e}")
            return render_template('error.html', error_message="Une erreur est survenue. Veuillez réessayer plus tard.")

    return app

# 📌 Exécution de l'application si ce fichier est lancé directement
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
