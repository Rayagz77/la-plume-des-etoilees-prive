import os
from flask import Blueprint, request, render_template, redirect, url_for, current_app
from controllers.access_management import admin_required, user_required, guest_required

from werkzeug.utils import secure_filename
from models.book_model import Book
from models.author_model import Author
from models.category_model import Category
from models import db

admin_bp = Blueprint('admin_bp', __name__)

# Tableau de bord
@admin_bp.route('/admin_dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# CRUD Books

# READ 
@admin_bp.route('/books', methods=['GET'])
@admin_required
def list_books():
    books = Book.query.all()
    return render_template('list_books.html', books=books)

# CREATE
@admin_bp.route('/add_book', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        # Vérifiez que toutes les données nécessaires sont envoyées
        try:
            title = request.form['title']
            publication_date = request.form['publication_date']
            price = float(request.form['price'])
            author_id = int(request.form['author_id'])
            category_id = int(request.form['category_id'])

            # Vérifiez si une image est fournie
            image_file = request.files['book_image']
            book_image_url = None
            if image_file:
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(current_app.root_path, 'static/images', filename)
                image_file.save(image_path)
                book_image_url = f'/static/images/{filename}'

            # Création d'un nouvel objet livre
            new_book = Book(
                book_title=title,
                publication_date=publication_date,
                book_price=price,
                author_id=author_id,
                category_id=category_id,
                book_image_url=book_image_url
            )
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('admin_bp.list_books'))
        except Exception as e:
            print("Erreur lors de l'ajout du livre :", e)
            return "Erreur lors de l'ajout du livre", 400

    authors = Author.query.all()
    categories = Category.query.all()
    return render_template('add_book.html', authors=authors, categories=categories)

# UPDATE
@admin_bp.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return "Livre introuvable", 404

    if request.method == 'POST':
        book.book_title = request.form['title']
        book.publication_date = request.form['publication_date']
        book.book_price = float(request.form['price'])
        book.author_id = int(request.form['author_id'])
        book.category_id = int(request.form['category_id'])
        db.session.commit()
        return redirect(url_for('admin_bp.list_books'))

    authors = Author.query.all()
    categories = Category.query.all()
    return render_template('edit_book.html', book=book, authors=authors, categories=categories)

# DELETE
@admin_bp.route('/delete_book/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return "Livre introuvable", 404

    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('admin_bp.list_books'))


# CRUD Authors
@admin_bp.route('/authors', methods=['GET'])
@admin_required
def list_authors():
    authors = Author.query.all()
    return render_template('list_authors.html', authors=authors)

@admin_bp.route('/add_author', methods=['GET', 'POST'])
@admin_required
def add_author():
    if request.method == 'POST':
        try:
            author_firstname = request.form['author_firstname']
            author_lastname = request.form['author_lastname']
            author_birthday = request.form['author_birthday']

            new_author = Author(
                author_firstname=author_firstname,
                author_lastname=author_lastname,
                author_birthday=author_birthday
            )
            db.session.add(new_author)
            db.session.commit()
            return redirect(url_for('admin_bp.list_authors'))
        except Exception as e:
            print("Erreur lors de l'ajout de l'auteur :", e)
            return "Erreur lors de l'ajout de l'auteur", 400

    return render_template('add_author.html')

@admin_bp.route('/edit_author/<int:author_id>', methods=['GET', 'POST'])
@admin_required
def edit_author(author_id):
    author = Author.query.get(author_id)
    if not author:
        return "Auteur introuvable", 404

    if request.method == 'POST':
        author.author_firstname = request.form['author_firstname']
        author.author_lastname = request.form['author_lastname']
        author.author_birthday = request.form['author_birthday']
        db.session.commit()
        return redirect(url_for('admin_bp.list_authors'))

    return render_template('edit_author.html', author=author)

@admin_bp.route('/delete_author/<int:author_id>', methods=['POST'])
@admin_required
def delete_author(author_id):
    author = Author.query.get(author_id)
    if not author:
        return "Auteur introuvable", 404

    db.session.delete(author)
    db.session.commit()
    return redirect(url_for('admin_bp.list_authors'))


# CRUD Categories
@admin_bp.route('/categories', methods=['GET'])
@admin_required
def list_categories():
    categories = Category.query.all()
    return render_template('list_categories.html', categories=categories)

@admin_bp.route('/add_category', methods=['GET', 'POST'])
@admin_required
def add_category():
    if request.method == 'POST':
        try:
            category_name = request.form['category_name']
            new_category = Category(category_name=category_name)
            db.session.add(new_category)
            db.session.commit()
            return redirect(url_for('admin_bp.list_categories'))
        except Exception as e:
            print("Erreur lors de l'ajout de la catégorie :", e)
            return "Erreur lors de l'ajout de la catégorie", 400

    return render_template('add_category.html')


@admin_bp.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return "Catégorie introuvable", 404

    if request.method == 'POST':
        category.category_name = request.form['category_name']
        db.session.commit()
        return redirect(url_for('admin_bp.list_categories'))

    return render_template('edit_category.html', category=category)

@admin_bp.route('/delete_category/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return "Catégorie introuvable", 404

    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('admin_bp.list_categories'))
