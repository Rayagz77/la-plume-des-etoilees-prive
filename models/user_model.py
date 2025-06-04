from . import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(50), nullable=False)
    user_lastname = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    user_signup_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_phone = db.Column(db.String(15), nullable=True)
    user_role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # Relations
    orders = db.relationship('Order', back_populates='user', cascade="all, delete-orphan")
    
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)  # Ajoutez cette ligne
    last_failed_login = db.Column(db.DateTime, nullable=True)  # Optionnel : date du dernier échec
    account_locked = db.Column(db.Boolean, default=False, nullable=False)  # Optionnel : verrouillage
    # Méthodes pour Flask-Login
    def get_id(self):
        return str(self.user_id)
    
    @property
    def is_authenticated(self):
        return True  # Tous les utilisateurs sont considérés comme authentifiés
    
    @property
    def is_anonymous(self):
        return False  # False car nous n'utilisons pas d'utilisateurs anonymes

    # Méthodes pour la gestion du mot de passe
    def set_password(self, password):
        self.user_password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.user_password, password)

    def __repr__(self):
        return f"<User {self.user_firstname} {self.user_lastname}>"
    
    def handle_failed_login(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Après 5 échecs
            self.account_locked = True
        db.session.commit()