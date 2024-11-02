from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(100), nullable=False)
    user_lastname = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(255), unique=True, nullable=False)
    user_signup_date = db.Column(db.Date, default=datetime.utcnow)
    user_password = db.Column(db.String(255), nullable=False)
    user_phone = db.Column(db.String(15))
