from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash

from models import db
from models.user_model import User
from controllers.access_management import guest_required

login_bp = Blueprint('login_bp', __name__)

# 🔐 Connexion
@login_bp.route('/login', methods=['GET', 'POST'])
@guest_required
def login():
    if request.method == 'POST':
        email = request.form.get('user_email')
        password = request.form.get('user_password')

        if not email or not password:
            flash('Veuillez remplir tous les champs.', 'warning')
            return redirect(url_for('login_bp.login'))

        user = User.query.filter_by(user_email=email).first()

        if user and check_password_hash(user.user_password, password):
            login_user(user)  # Flask-Login authentifie
            session['user_id'] = user.user_id
            session['user_firstname'] = user.user_firstname
            flash(f"🤗 Ravie de vous revoir {user.user_firstname} !", 'success')

            # ✅ Redirection selon le rôle
            if user.user_role == 'admin':
                return redirect(url_for('admin_bp.admin_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
            return redirect(url_for('login_bp.login'))

    return render_template('login.html')

# 🔓 Déconnexion
@login_bp.route('/logout')
def logout():
    logout_user()          # Flask-Login : retire current_user
    session.clear()        # Nettoie la session Flask
    flash("👋 Vous avez été déconnecté avec succès.", "info")
    return redirect(url_for('home'))
