from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from models import db  # Ajoutez cette ligne pour éviter d'avoir un problème avec db
from models.user_model import User

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('user_email')
        password = request.form.get('user_password')

        if not email or not password:
            flash('Veuillez remplir tous les champs.', 'warning')
            return redirect(url_for('login_bp.login'))

        user = db.session.query(User).filter_by(user_email=email).first()  # UTILISEZ db.session.query()

        if user and check_password_hash(user.user_password, password):
            session['user_id'] = user.user_id
            session['user_firstname'] = user.user_firstname
            flash(f"🤗 Ravie de vous revoir {user.user_firstname} !", 'success')
            return redirect(url_for('home'))  
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
            return redirect(url_for('login_bp.login'))

    return render_template('login.html')
