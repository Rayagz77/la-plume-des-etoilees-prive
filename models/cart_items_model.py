from . import db

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    cart_item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)

    # Relations
    user = db.relationship('User', back_populates='cart_items')
    book = db.relationship('Book', back_populates='cart_items')

    def __repr__(self):
        return f"<CartItem {self.cart_item_id} user={self.user_id} book={self.book_id}>"
