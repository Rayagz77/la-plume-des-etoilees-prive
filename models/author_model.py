from . import db
from datetime import datetime

class Author(db.Model):
    __tablename__ = 'Author'  # Nom exact de la table
    author_id = db.Column(db.Integer, primary_key=True)
    author_firstname = db.Column(db.String(100), nullable=False)
    author_lastname = db.Column(db.String(100), nullable=False)
    author_birthday = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Author {self.author_firstname} {self.author_lastname}>"
