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
