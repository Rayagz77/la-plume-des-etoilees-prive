from flask import Flask, render_template, request
from dotenv import load_dotenv
from flask_migrate import Migrate
import os
import sys

# Ajouter le chemin du répertoire racine pour que Python trouve le module 'models'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db
from models.book_model import Book
from models.category_model import Category
from models.author_model import Author
from controllers.register_controller import register_bp
from controllers.auth_controller import login_bp
from controllers.admin_controller import admin_bp

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuration de la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('SECRET_KEY')

    # Initialiser la base de données
    db.init_app(app)

    # Initialiser Flask-Migrate pour gérer les migrations
    migrate = Migrate(app, db)

    # Enregistrer les Blueprints avec des préfixes
    app.register_blueprint(register_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Important

    @app.route('/')
    def home():
        try:
            # Récupération du paramètre de catégorie (si sélectionné)
            selected_category_id = request.args.get('category', type=int)
            
            # Utilisation de la pagination
            page = request.args.get('page', 1, type=int)
            per_page = 9

            # Si une catégorie est sélectionnée, filtrer les livres par cette catégorie
            if selected_category_id:
                pagination = Book.query.filter_by(category_id=selected_category_id).paginate(page=page, per_page=per_page, error_out=False)
            else:
                pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)

            books = pagination.items

            # Récupérer toutes les catégories
            categories = Category.query.all()

            return render_template('home.html', books=books, pagination=pagination, categories=categories, selected_category_id=selected_category_id)
        except Exception as e:
            print("Error:", e)
            return str(e)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
