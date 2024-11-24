# models/cart_model.py
from . import db

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('Book.book_id'), nullable=False)

    # Relations
    book = db.relationship('Book', back_populates='cart_items')  # Utilisez le même back_populates que dans Book
