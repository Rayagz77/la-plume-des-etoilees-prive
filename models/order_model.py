from . import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'Orders'  # Table avec majuscule

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')

    # Relation avec User
    user = db.relationship('User', back_populates='orders')

    # Relation avec OrderDetail (sans import direct)
    details = db.relationship('OrderDetail', back_populates='order', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.order_id} - User {self.user_id}>"
