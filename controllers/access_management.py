from flask import redirect, url_for, flash
from flask_login import current_user, login_required
from functools import wraps

# Décorateurs pour gérer les accès

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("🧪 Rôle détecté :", getattr(current_user, 'user_role', 'Aucun'))

        if not current_user.is_authenticated or current_user.user_role != 'admin':
            flash("Accès refusé. Vous devez être administrateur.", "danger")
            return redirect(url_for("login_bp.login"))
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter pour accéder à cette page.", "warning")
            return redirect(url_for("login_bp.login"))
        return f(*args, **kwargs)
    return decorated_function

def guest_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("Vous êtes déjà connecté.", "info")
            return redirect(url_for("home"))  # Modifier selon votre route principale
        return f(*args, **kwargs)
    return decorated_function
