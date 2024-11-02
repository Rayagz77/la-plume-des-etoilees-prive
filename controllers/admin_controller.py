import os

from flask import Blueprint, request, render_template, redirect, url_for, current_app, request

from werkzeug.utils import secure_filename
from models.book_model import Book
from models.author_model import Author
from models.category_model import Category
from models import db
from math import ceil

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        title = request.form['title']
        publication_date = request.form['publication_date']
        price = float(request.form['price'])
        author_id = int(request.form['author_id'])
        category_id = int(request.form['category_id'])

        # Gérer le téléchargement de l'image
        image_file = request.files['book_image']
        if image_file:
            # Sécuriser le nom du fichier et définir le chemin de stockage
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.root_path, 'static/images', filename)
            image_file.save(image_path)
            book_image_url = f'/static/images/{filename}'
        else:
            book_image_url = None

        # Créer un nouvel objet livre
        new_book = Book(
            book_title=title,
            publication_date=publication_date,
            book_price=price,
            author_id=author_id,
            category_id=category_id,
            book_image_url=book_image_url
        )

        # Ajouter à la base de données
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('admin_bp.books'))  # Rediriger vers la page d'accueil

    # Récupérer les auteurs et catégories pour le formulaire
    authors = Author.query.all()
    categories = Category.query.all()

    # Assurez-vous de bien transmettre les auteurs et catégories au template
    return render_template('add_book.html', authors=authors, categories=categories)

# Route pour ajouter un auteur
@admin_bp.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        author_firstname = request.form['author_firstname']
        author_lastname = request.form['author_lastname']
        author_birthday = request.form['author_birthday']

        # Créer un nouvel objet Author
        new_author = Author(
            author_firstname=author_firstname,
            author_lastname=author_lastname,
            author_birthday=author_birthday
        )

        # Ajouter l'auteur à la base de données
        db.session.add(new_author)
        db.session.commit()

        return redirect(url_for('admin_bp.add_book'))  # Rediriger vers la page d'ajout de livre

    return render_template('add_author.html')  # Afficher le formulaire pour ajouter un auteur

# Route pour ajouter une catégorie
@admin_bp.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        category_name = request.form['category_name']

        # Créer un nouvel objet Category
        new_category = Category(
            category_name=category_name
        )

        # Ajouter la catégorie à la base de données
        db.session.add(new_category)
        db.session.commit()

        return redirect(url_for('admin_bp.add_book'))  # Rediriger vers la page d'ajout de livre

    return render_template('add_category.html')  # Afficher le formulaire pour ajouter une catégorie

# Route pour afficher les livres avec pagination
@admin_bp.route('/pagination_books', methods=['GET'])
def pagination_books():
    # Récupérer les livres avec pagination
    page = request.args.get('page', 1, type=int)
    per_page = 9
    pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items

    return render_template('pagination_books.html', books=books, pagination=pagination)

# Correction du problème d'importation
if __name__ == "__main__":
    from models import db
    db.create_all()
