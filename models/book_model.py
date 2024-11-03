# models/book_model.py
from . import db
from datetime import datetime
from models.author_model import Author
from models.category_model import Category

class Book(db.Model):
    __tablename__ = 'Book'
    book_id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String, nullable=False)
    publication_date = db.Column(db.Date, nullable=False)
    book_price = db.Column(db.Float, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('Author.author_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('Category.category_id'), nullable=False)  # Clé étrangère vers Category
    book_image_url = db.Column(db.String, nullable=True)

    # Relations
    author = db.relationship('Author', backref='books')
    category = db.relationship('Category', backref='books')  # Relation avec Category

    def __repr__(self):
        return f"<Book {self.book_title} by author_id {self.author_id}>"
