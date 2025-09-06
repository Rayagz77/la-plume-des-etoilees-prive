from . import db

class Book(db.Model):
    __tablename__ = 'book'

    book_id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(255), nullable=False)
    publication_date = db.Column(db.Date, nullable=False)
    book_price = db.Column(db.Float, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('author.author_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    book_image_url = db.Column(db.String, nullable=True)

    # Relations
    author = db.relationship('Author', back_populates='books')
    category = db.relationship('Category', back_populates='books')
    cart_items = db.relationship('CartItem', back_populates='book', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book {self.book_title}>"
