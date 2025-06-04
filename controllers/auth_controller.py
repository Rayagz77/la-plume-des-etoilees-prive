from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
import time
import os

from models import db
from models.user_model import User
from controllers.access_management import guest_required
# controllers/auth_controller.py
from extensions.mongo import log_login, log_action, get_mongo

login_bp = Blueprint('login_bp', __name__)

# Configuration sécurité
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes

@login_bp.route('/login', methods=['GET', 'POST'])
@guest_required
def login():
    if request.method == 'POST':
        email = request.form.get('user_email', '').strip().lower()
        password = request.form.get('user_password', '')
        ip_addr = request.remote_addr  # IP du client

        # Gestion des tentatives
        session['login_attempts'] = session.get('login_attempts', 0) + 1
        if session['login_attempts'] > MAX_LOGIN_ATTEMPTS:
            flash('Trop de tentatives. Veuillez réessayer plus tard.', 'danger')
            try:
                log_login(None, email, None, "locked", ip_addr)
            except Exception as e:
                print(f"⚠️ log_login failed (locked): {e}")
            return redirect(url_for('login_bp.login'))

        user = User.query.filter_by(user_email=email).first()

        if user and check_password_hash(user.user_password, password):
            session['login_attempts'] = 0
            login_user(user)
            session['user_id'] = user.user_id
            session['user_firstname'] = user.user_firstname
            print("✅ Authentification réussie : appel de log_login()")
            
            try:
                log_login(user.user_id, email, user.user_role, "success", ip_addr)
            except Exception as e:
                print(f"⚠️ log_login failed (success): {e}")

            flash(f"Bienvenue {user.user_firstname} !", 'success')
            return redirect(url_for(
                'admin_bp.admin_dashboard' if user.user_role == 'admin' else 'home'
            ))
        else:
            try:
                log_login(
                    user.user_id if user else None,
                    email,
                    user.user_role if user else None,
                    "fail",
                    ip_addr
                )
            except Exception as e:
                print(f"⚠️ log_login failed (fail): {e}")

            flash('Email ou mot de passe incorrect', 'danger')
            return redirect(url_for('login_bp.login'))

    return render_template('login.html')


@login_bp.route('/logout')
@login_required
def logout():
    try:
        log_action(
            user_id=current_user.user_id,
            email=current_user.user_email,
            role=current_user.user_role,
            action_type="logout"
        )
    except Exception as e:
        print(f"⚠️ log_action failed (logout): {e}")

    logout_user()
    session.clear()
    flash("Vous avez été déconnecté", "info")
    return redirect(url_for('home'))


@login_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(user_email=email).first()
        if user:
            serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('login_bp.reset_password', token=token, _external=True)
            # send_reset_email(user.user_email, reset_url)

        flash('Si un compte existe avec cet email, vous recevrez un lien de réinitialisation', 'info')
        return redirect(url_for('login_bp.login'))

    return render_template('login.html', show_forgot_modal=True)


@login_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('Le lien de réinitialisation est invalide ou a expiré', 'danger')
        return redirect(url_for('login_bp.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'danger')
            return redirect(request.url)

        user = User.query.filter_by(user_email=email).first()
        if user:
            user.user_password = generate_password_hash(password)
            db.session.commit()
            flash('Votre mot de passe a été mis à jour. Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login_bp.login'))

    return render_template('reset_password.html', token=token)
