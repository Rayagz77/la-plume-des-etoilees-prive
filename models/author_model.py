from . import db
from datetime import datetime

class Author(db.Model):
    __tablename__ = 'author'
    author_id = db.Column(db.Integer, primary_key=True)
    author_firstname = db.Column(db.String(100), nullable=False)
    author_lastname = db.Column(db.String(100), nullable=False)
    author_birthday = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    books = db.relationship('Book', back_populates='author', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Author {self.author_firstname} {self.author_lastname}>"
