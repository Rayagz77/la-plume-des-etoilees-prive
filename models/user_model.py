from . import db

class User(db.Model):
    __tablename__ = 'User'  # Nom exact de la table
    user_id = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(50), nullable=False)
    user_lastname = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    user_signup_date = db.Column(db.DateTime, nullable=False)
    # Ajoutez 'user_phone' si nécessaire
    user_phone = db.Column(db.String(15), nullable=True)
