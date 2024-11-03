# Flask Blueprint for Register
from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models.user_model import User
from models import db
from datetime import datetime
import re

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['user_firstname']
        lastname = request.form['user_lastname']
        email = request.form['user_email']
        password = request.form['user_password']
        phone = request.form.get('user_phone')

        # Server-side validation
        if len(firstname) < 3 or len(lastname) < 3:
            flash("Le prénom et le nom de famille doivent contenir au moins 3 caractères.", "danger")
            return redirect(url_for('register.register'))

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            flash("Veuillez entrer une adresse email valide.", "danger")
            return redirect(url_for('register.register'))

        if len(password) < 12:
            flash("Le mot de passe doit contenir au moins 12 caractères.", "danger")
            return redirect(url_for('register.register'))

        phone_pattern = r"^\+?\d{7,15}$"
        if phone and not re.match(phone_pattern, phone):
            flash("Veuillez entrer un numéro de téléphone valide.", "danger")
            return redirect(url_for('register.register'))

        # Hash the password
        password_hashed = generate_password_hash(password)

        # Check if the email already exists
        existing_user = User.query.filter_by(user_email=email).first()
        if existing_user:
            flash("Cet email est déjà utilisé.", "danger")
            return redirect(url_for('register.register'))

        # Create a new user
        new_user = User(
            user_firstname=firstname,
            user_lastname=lastname,
            user_email=email,
            user_signup_date=datetime.utcnow(),
            user_password=password_hashed,
            user_phone=phone
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Inscription réussie, vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for('login.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'inscription : {str(e)}", "danger")
            return redirect(url_for('register.register'))

    return render_template('register.html')
