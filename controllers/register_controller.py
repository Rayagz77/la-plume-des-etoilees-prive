from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models.user_model import User
from models import db
from datetime import datetime

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['user_firstname']
        lastname = request.form['user_lastname']
        email = request.form['user_email']
        password = generate_password_hash(request.form['user_password'])
        phone = request.form.get('user_phone')

        new_user = User(
            user_firstname=firstname,
            user_lastname=lastname,
            user_email=email,
            user_signup_date=datetime.utcnow(),
            user_password=password,
            user_phone=phone
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash("Erreur lors de l'inscription : cet email est déjà utilisé.", "danger")
            return redirect(url_for('register.register'))

    return render_template('register.html')
