import os
from . import db
from datetime import datetime
from models.author_model import Author
from models.category_model import Category

class Book(db.Model):
    __tablename__ = 'books'  # Utilisation d'un nom de table en minuscules et au pluriel pour uniformité
    book_id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String, nullable=False)
    publication_date = db.Column(db.Date, nullable=False)
    book_price = db.Column(db.Float, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'), nullable=False)  # Notez l'utilisation de 'authors'
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)  # Notez l'utilisation de 'categories'
    book_image_url = db.Column(db.String, nullable=True)

    author = db.relationship('Author', backref='books')
    category = db.relationship('Category', backref='books', primaryjoin='Book.category_id == Category.category_id')

    def __repr__(self):
        return f"<Book {self.book_title} by author_id {self.author_id}>"

import os
import sys

from flask import Flask, render_template, request, jsonify  # Import de request pour gérer les paramètres de pagination
from dotenv import load_dotenv
from flask_migrate import Migrate
from sqlalchemy import func
# Ajouter le chemin du répertoire racine du projet
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models import db  # Importer db depuis models/__init__.py
from models.book_model import Book
from models.category_model import Category
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
            # Récupérer toutes les catégories
            categories = Category.query.all()

            # Utiliser la pagination pour afficher 12 livres par page
            page = request.args.get('page', 1, type=int)
            per_page = 9
            pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
            books = pagination.items

            return render_template('home.html', books=books, categories=categories, pagination=pagination)
        except Exception as e:
            print("Error:", e)
            return str(e)

    @app.route('/filter_books', methods=['GET'])
    def filter_books():
        try:
            # Récupérer la catégorie choisie
            category_name = request.args.get('category', type=str)
            print(f"Catégorie choisie: {category_name}")

            # Filtrer les livres par catégorie (insensible à la casse)
            if category_name:
                category = Category.query.filter(func.lower(Category.category_name) == category_name.lower()).first()
                if category:
                    books = Book.query.filter(Book.category_id == category.category_id).all()
                    print(f"Livres trouvés: {len(books)}")
                else:
                    books = []
                    print("Aucune catégorie trouvée")
            else:
                books = Book.query.all()
                print(f"Nombre total de livres: {len(books)}")

            # Préparer les données des livres à renvoyer
            books_data = [
                {
                    'book_title': book.book_title,
                    'author_firstname': book.author.author_firstname,
                    'author_lastname': book.author.author_lastname,
                    'book_price': book.book_price,
                    'book_image_url': book.book_image_url
                }
                for book in books
            ]

            return jsonify(books_data)
        except Exception as e:
            print("Error:", e)
            return jsonify({'error': str(e)})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
