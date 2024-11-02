from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from models.user_model import User
from models import db

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['user_email']
        password = request.form['user_password']
        
        # Query the database for the user
        user = User.query.filter_by(user_email=email).first()
        
        if user and check_password_hash(user.user_password, password):
            # Store the user's ID and first name in the session
            session['user_id'] = user.user_id
            session['user_firstname'] = user.user_firstname
            flash('Connexion réussie!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html')

@login_bp.route('/logout')
def logout():
    session.clear()  # Clear the user's session
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('login.login'))
