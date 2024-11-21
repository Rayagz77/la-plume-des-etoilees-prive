import os
from flask import Blueprint, request, render_template, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from models.book_model import Book
from models.author_model import Author
from models.category_model import Category
from models import db

admin_bp = Blueprint('admin_bp', __name__)

# Tableau de bord
@admin_bp.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    return render_template('admin_dashboard.html')

# CRUD Books
@admin_bp.route('/books', methods=['GET'])
def list_books():
    books = Book.query.all()
    return render_template('list_books.html', books=books)

@admin_bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        publication_date = request.form['publication_date']
        price = float(request.form['price'])
        author_id = int(request.form['author_id'])
        category_id = int(request.form['category_id'])

        image_file = request.files['book_image']
        book_image_url = None
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.root_path, 'static/images', filename)
            image_file.save(image_path)
            book_image_url = f'/static/images/{filename}'

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

    authors = Author.query.all()
    categories = Category.query.all()
    return render_template('add_book.html', authors=authors, categories=categories)

# CRUD Authors
@admin_bp.route('/authors', methods=['GET'])
def list_authors():
    try:
        authors = Author.query.all()  # Récupérer tous les auteurs
        print("Auteurs récupérés :", authors)  # Debug
        return render_template('list_authors.html', authors=authors)
    except Exception as e:
        return f"Erreur lors de la récupération des auteurs : {e}", 500


@admin_bp.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
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
    return render_template('add_author.html')

# CRUD Categories
@admin_bp.route('/categories', methods=['GET'])
def list_categories():
    try:
        categories = Category.query.all()  # Récupérer toutes les catégories
        print("Catégories récupérées :", categories)  # Debug
        return render_template('list_categories.html', categories=categories)
    except Exception as e:
        return f"Erreur lors de la récupération des catégories : {e}", 500

@admin_bp.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category_name = request.form['category_name']
        new_category = Category(category_name=category_name)
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('admin_bp.list_categories'))
    return render_template('add_category.html')
