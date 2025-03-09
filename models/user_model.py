from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'User'  # Table "User" en majuscule

    user_id = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(50), nullable=False)
    user_lastname = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    user_signup_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_phone = db.Column(db.String(15), nullable=True)

    # Relation avec Orders (Un utilisateur peut avoir plusieurs commandes)
    orders = db.relationship('Order', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.user_firstname} {self.user_lastname}>"
