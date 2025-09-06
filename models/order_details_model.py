from . import db

class OrderDetail(db.Model):
    __tablename__ = 'order_details'

    order_details_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)

    # Relations
    order = db.relationship('Order', back_populates='details')
    book = db.relationship('Book')

    def __repr__(self):
        return f"<OrderDetail {self.order_details_id} - Order {self.order_id} - Book {self.book_id}>"
