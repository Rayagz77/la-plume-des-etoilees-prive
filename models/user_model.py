from . import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(50), nullable=False)
    user_lastname = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    user_signup_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_phone = db.Column(db.String(15), nullable=True)
    user_role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    last_failed_login = db.Column(db.DateTime, nullable=True)
    account_locked = db.Column(db.Boolean, default=False, nullable=False)

    # Relations
    orders = db.relationship('Order', back_populates='user', cascade="all, delete-orphan")
    cart_items = db.relationship('CartItem', back_populates='user', cascade="all, delete-orphan")

    @property
    def id(self):
        # Alias pour compatibilité avec current_user.id
        return self.user_id

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.user_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.user_password, password)

    def __repr__(self):
        return f"<User {self.user_firstname} {self.user_lastname}>"

    def handle_failed_login(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.account_locked = True
        db.session.commit()
