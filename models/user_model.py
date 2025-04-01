from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(50), nullable=False)
    user_lastname = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    user_signup_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_phone = db.Column(db.String(15), nullable=True)

    # ✅ Ajoute ce champ :
    user_role = db.Column(db.String(20), default='user')  # valeurs possibles : 'user', 'admin'

    # Relations
    orders = db.relationship('Order', back_populates='user', cascade="all, delete-orphan")

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f"<User {self.user_firstname} {self.user_lastname}>"
