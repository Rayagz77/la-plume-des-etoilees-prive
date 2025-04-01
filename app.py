import os
import sys
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from flask_login import LoginManager

from flask_migrate import Migrate
import stripe

# 📌 Ajouter le dossier courant pour permettre les imports relatifs
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 📌 Charger les variables d'environnement (.env)
load_dotenv()

# 📌 Importer les modules internes
from models import db
from models.book_model import Book
from models.user_model import User
from models.category_model import Category
from models.author_model import Author
from models.cart_items_model import CartItem
from models.order_details_model import OrderDetail

from controllers.access_management import admin_required, user_required, guest_required
from controllers.register_controller import register_bp
from controllers.auth_controller import login_bp
from controllers.admin_controller import admin_bp
from controllers.cart_controller import cart_bp
from controllers.payement_controller import payement_bp
from controllers.account_controller import account_bp

# 📌 Configuration Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise ValueError("❌ STRIPE_SECRET_KEY doit être défini dans le fichier .env")

# 📌 Créer l'application Flask
def create_app():
    app = Flask(__name__)

    # 📌 Configuration de l'application
    db_uri = os.getenv("DATABASE_URI")
    secret_key = os.getenv("SECRET_KEY")

    if not db_uri:
        raise ValueError("❌ DATABASE_URI doit être défini dans le fichier .env")
    if not secret_key:
        raise ValueError("❌ SECRET_KEY doit être défini dans le fichier .env")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = secret_key

    # 📌 Initialiser les extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # ✅ INITIALISATION FLASK-LOGIN
  
 # ✅ INITIALISATION FLASK-LOGIN
    login_manager = LoginManager()
    login_manager.init_app(app)  # C’est cette ligne qui rend current_user utilisable
    login_manager.login_view = 'login_bp.login'
    login_manager.login_message_category = "warning"

    # ✅ Important : user_loader ici
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # 📌 Blueprints
    app.register_blueprint(register_bp, url_prefix='/register')
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(payement_bp, url_prefix='/payement')
    app.register_blueprint(account_bp, url_prefix='/account')

    # 📌 Variables accessibles dans tous les templates
    @app.context_processor
    def inject_cart_data():
        if 'user_id' in session:
            cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
            total_price = sum(item.book.book_price for item in cart_items)
            return {
                'cart_items': cart_items,
                'total_price': total_price,
                'cart_count': len(cart_items)
            }
        return {'cart_items': [], 'total_price': 0, 'cart_count': 0}

    # 📌 Page d'accueil
    @app.route('/')
    def home():
        return render_template('home.html')

    # 📌 Galerie de livres
    @app.route('/books')
    def gallery():
        try:
            selected_category_id = request.args.get('category', type=int)
            page = request.args.get('page', 1, type=int)
            per_page = 9

            query = Book.query
            if selected_category_id:
                query = query.filter_by(category_id=selected_category_id)

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            return render_template('gallery.html',
                                   books=pagination.items,
                                   pagination=pagination,
                                   categories=Category.query.all(),
                                   selected_category_id=selected_category_id)
        except Exception as e:
            print(f"⚠️ Erreur dans gallery(): {e}")
            return render_template('error.html', error_message="Une erreur est survenue.")

    return app

# 📌 Exécution
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
