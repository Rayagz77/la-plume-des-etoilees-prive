from flask import Flask, render_template, request, session
from dotenv import load_dotenv
from flask_migrate import Migrate
import os
import sys

# Ajouter le chemin du répertoire racine pour les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer les modèles et contrôleurs
from models import db
from models.book_model import Book
from models.category_model import Category
from models.author_model import Author
from models.cart_items_model import CartItem
from controllers.register_controller import register_bp
from controllers.auth_controller import login_bp
from controllers.admin_controller import admin_bp
from controllers.cart_controller import cart_bp

# Charger les variables d'environnement
load_dotenv()

def create_app(config_name='default'):
    app = Flask(__name__)

    # Configuration par environnement
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de données en mémoire
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True
        app.secret_key = 'testsecret'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.secret_key = os.getenv('SECRET_KEY')

    # Initialisation de la base de données
    db.init_app(app)
    migrate = Migrate(app, db)

    # Enregistrement des blueprints
    app.register_blueprint(register_bp, url_prefix='/register')
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cart_bp, url_prefix='/cart')

    # Ajouter un processeur de contexte global
    @app.context_processor
    def inject_cart_count():
        user_id = session.get('user_id')
        cart_count = 0
        if user_id:
            cart_count = CartItem.query.filter_by(user_id=user_id).count()
        return {'cart_count': cart_count}

    # Route principale
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/books')
    def gallery():
        try:
            # Récupération de la catégorie et de la page
            selected_category_id = request.args.get('category', type=int)
            page = request.args.get('page', 1, type=int)
            per_page = 9  # Nombre de livres par page

            # Filtrer par catégorie si selected_category_id est présent
            if selected_category_id:
                pagination = Book.query.filter_by(category_id=selected_category_id)\
                                    .paginate(page=page, per_page=per_page, error_out=False)
            else:
                pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)

            # Liste des livres pour la page courante
            books = pagination.items

            # Liste de toutes les catégories pour le filtre
            categories = Category.query.all()

            # On renvoie la page de gallery
            return render_template('gallery.html',
                                   books=books,
                                   pagination=pagination,
                                   categories=categories,
                                   selected_category_id=selected_category_id)
        except Exception as e:
            print(f"Error in gallery(): {e}")
            return render_template('error.html', error_message="Une erreur est survenue. Veuillez réessayer plus tard.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
