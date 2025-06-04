from flask import redirect, url_for, flash, current_app, request
from flask_login import current_user
from functools import wraps
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

def admin_required(f):
    """Décorateur pour les routes réservées aux administrateurs"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log de débogage
        logger.debug(f"Tentative d'accès admin à {request.path} par {current_user.user_email if current_user.is_authenticated else 'anonyme'}")
        
        if not current_user.is_authenticated:
            flash("Authentification requise pour cette zone", "danger")
            logger.warning("Tentative d'accès non authentifiée à une zone admin")
            return redirect(url_for("login_bp.login", next=request.url))
            
        if current_user.user_role != 'admin':
            flash("Privilèges insuffisants - Accès réservé aux administrateurs", "danger")
            logger.warning(f"Tentative d'accès non autorisée par {current_user.user_email} (rôle: {current_user.user_role})")
            return redirect(url_for("home"))
            
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    """Décorateur pour les utilisateurs connectés (non admins)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter pour accéder à cette page", "warning")
            return redirect(url_for("login_bp.login", next=request.url))
            
        if current_user.user_role == 'admin':
            flash("Les administrateurs doivent utiliser le panel admin", "info")
            return redirect(url_for("admin_bp.dashboard"))
            
        return f(*args, **kwargs)
    return decorated_function


def guest_required(f):
    """Décorateur pour les visiteurs non connectés"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            user_type = "administrateur" if current_user.user_role == 'admin' else "utilisateur"
            flash(f"Vous êtes déjà connecté en tant que {user_type}", "info")
            return redirect(url_for("home"))
            
        return f(*args, **kwargs)
    return decorated_function


def role_required(required_role):
    """Décorateur générique pour la gestion des rôles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Authentification requise", "danger")
                return redirect(url_for("login_bp.login"))
                
            if current_user.user_role != required_role:
                flash(f"Accès réservé aux {required_role}s", "danger")
                return redirect(url_for("home"))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Version alternative avec gestion des permissions multiples
def has_role(roles):
    """Décorateur acceptant plusieurs rôles"""
    if isinstance(roles, str):
        roles = [roles]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Accès non autorisé", "danger")
                return redirect(url_for("login_bp.login"))
                
            if current_user.user_role not in roles:
                flash("Privilèges insuffisants", "danger")
                return redirect(url_for("home"))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator