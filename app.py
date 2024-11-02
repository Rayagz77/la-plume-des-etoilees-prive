import os
import sys

from flask import Flask, render_template, request  # Import de request pour gérer les paramètres de pagination
from dotenv import load_dotenv
from flask_migrate import Migrate

# Ajouter le chemin du répertoire racine du projet
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models import db  # Importer db depuis models/__init__.py
from models.book_model import Book
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

    # Enregistrer les Blueprints
    app.register_blueprint(register_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def home():
        try:
            # Utiliser la pagination pour afficher 12 livres par page
            page = request.args.get('page', 1, type=int)
            per_page = 9
            pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
            books = pagination.items
            return render_template('home.html', books=books, pagination=pagination)
        except Exception as e:
            print("Error:", e)
            return str(e)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
