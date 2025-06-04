from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from controllers.access_management import admin_required, user_required, guest_required
from werkzeug.security import generate_password_hash
from models.user_model import User
from models import db
from datetime import datetime
import re
import zxcvbn  # Module pour l'analyse de force des mots de passe

register_bp = Blueprint('register_bp', __name__)

def validate_password_strength(password):
    """Valide la force du mot de passe selon plusieurs critères"""
    errors = []
    requirements = {
        'length': len(password) >= 12,
        'uppercase': re.search(r'[A-Z]', password) is not None,
        'lowercase': re.search(r'[a-z]', password) is not None,
        'digit': re.search(r'\d', password) is not None,
        'special': re.search(r'[^A-Za-z0-9]', password) is not None,
        'common': not zxcvbn.zxcvbn(password)['score'] < 3  # Score minimum de 3/4
    }
    
    if not all(requirements.values()):
        if not requirements['length']:
            errors.append("Le mot de passe doit contenir au moins 12 caractères")
        if not requirements['uppercase']:
            errors.append("Le mot de passe doit contenir au moins une majuscule")
        if not requirements['lowercase']:
            errors.append("Le mot de passe doit contenir au moins une minuscule")
        if not requirements['digit']:
            errors.append("Le mot de passe doit contenir au moins un chiffre")
        if not requirements['special']:
            errors.append("Le mot de passe doit contenir au moins un caractère spécial")
        if not requirements['common']:
            errors.append("Le mot de passe est trop commun ou facile à deviner")
    
    return len(errors) == 0, errors

@register_bp.route('/check_password', methods=['POST'])
def check_password():
    """Endpoint pour la validation en temps réel du mot de passe"""
    password = request.form.get('password', '')
    is_valid, errors = validate_password_strength(password)
    
    # Analyse détaillée avec zxcvbn
    password_analysis = zxcvbn.zxcvbn(password)
    score = password_analysis['score']  # 0-4 (faible à fort)
    feedback = password_analysis['feedback']['suggestions']
    
    return jsonify({
        'valid': is_valid,
        'errors': errors,
        'score': score,
        'feedback': feedback,
        'crack_time': password_analysis['crack_times_display']['offline_slow_hashing_1e4_per_second']
    })

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # 1. Récupération et nettoyage des données
            firstname = request.form['user_firstname'].strip()
            lastname = request.form['user_lastname'].strip()
            email = request.form['user_email'].strip().lower()
            password = request.form['user_password']
            phone = request.form.get('user_phone', '').strip() or None  # Conversion explicite en None si vide

            # 2. Validation renforcée
            errors = []
            
            # Validation des noms
            if not re.match(r'^[a-zA-ZÀ-ÿ\s-]{2,50}$', firstname):
                errors.append("Prénom invalide (2-50 lettres, accents autorisés)")
            
            if not re.match(r'^[a-zA-ZÀ-ÿ\s-]{2,50}$', lastname):
                errors.append("Nom invalide (2-50 lettres, accents autorisés)")
            
            # Validation email
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("Format d'email invalide")
            
            # Validation mot de passe
            if len(password) < 12:
                errors.append("Le mot de passe doit contenir au moins 12 caractères")
            elif not any(c.isupper() for c in password):
                errors.append("Le mot de passe doit contenir au moins une majuscule")
            
            # Validation téléphone (optionnel)
            if phone and not re.match(r'^\+?[\d\s-]{7,15}$', phone):
                errors.append("Format de téléphone invalide (ex: +33 6 12 34 56 78)")

            # 3. Gestion des erreurs
            if errors:
                for error in errors:
                    flash(error, 'danger')
                return redirect(url_for('register_bp.register'))
            
            # Consentement explicite à la collecte de données
            if not request.form.get('consent_data'):
                flash("Vous devez accepter la collecte de vos données personnelles pour vous inscrire.", 'danger')
                return redirect(url_for('register_bp.register'))


            # 4. Vérification unicité email
            if User.query.filter_by(user_email=email).first():
                flash("Un compte existe déjà avec cet email", 'danger')
                return redirect(url_for('register_bp.register'))

            # 5. Création de l'utilisateur
            new_user = User(
                user_firstname=firstname,
                user_lastname=lastname,
                user_email=email,
                user_phone=phone  # None si vide
            )
            new_user.set_password(password)  # Hachage sécurisé

            # 6. Enregistrement
            db.session.add(new_user)
            db.session.commit()

            # 7. Redirection avec message
            flash("Votre compte a été créé avec succès !", 'success')
            return redirect(url_for('login_bp.login'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur inscription: {str(e)}", exc_info=True)
            flash("Une erreur technique est survenue. Veuillez réessayer.", 'danger')
            return redirect(url_for('register_bp.register'))

    # GET Request - Affichage du formulaire
    return render_template('register.html')