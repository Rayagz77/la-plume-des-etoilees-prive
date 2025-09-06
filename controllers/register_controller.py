from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, current_app
from models.user_model import User
from models import db
import re

# zxcvbn optionnel (no-crash si absent)
try:
    from zxcvbn import zxcvbn as _zxcvbn
except Exception:
    _zxcvbn = None

register_bp = Blueprint('register_bp', __name__)

# ---------------- Helpers ----------------

def analyze_password(pwd: str) -> dict:
    """Retourne {score, feedback, crack_time} ; fallback si zxcvbn absent."""
    if _zxcvbn:
        res = _zxcvbn(pwd)
        return {
            "score": res.get("score", 0),
            "feedback": res.get("feedback", {}).get("suggestions", []),
            "crack_time": res.get("crack_times_display", {}).get("offline_slow_hashing_1e4_per_second", "n/a"),
        }

    suggestions, score = [], 0
    if len(pwd) >= 12: score += 1
    else: suggestions.append("Utilise au moins 12 caractères")
    if any(c.isupper() for c in pwd): score += 1
    else: suggestions.append("Ajoute une majuscule")
    if any(c.isdigit() for c in pwd): score += 1
    else: suggestions.append("Ajoute un chiffre")
    if any(not c.isalnum() for c in pwd): score += 1
    else: suggestions.append("Ajoute un caractère spécial")
    return {"score": min(score, 4), "feedback": suggestions, "crack_time": "n/a"}

def validate_password_strength(password: str):
    errors = []
    analysis = analyze_password(password)
    score = analysis["score"]
    requirements = {
        "length": len(password) >= 12,
        "uppercase": re.search(r"[A-Z]", password) is not None,
        "lowercase": re.search(r"[a-z]", password) is not None,
        "digit": re.search(r"\d", password) is not None,
        "special": re.search(r"[^A-Za-z0-9]", password) is not None,
        "common": score >= 3,  # exige score >= 3/4
    }
    if not all(requirements.values()):
        if not requirements["length"]: errors.append("Le mot de passe doit contenir au moins 12 caractères")
        if not requirements["uppercase"]: errors.append("Le mot de passe doit contenir au moins une majuscule")
        if not requirements["lowercase"]: errors.append("Le mot de passe doit contenir au moins une minuscule")
        if not requirements["digit"]: errors.append("Le mot de passe doit contenir au moins un chiffre")
        if not requirements["special"]: errors.append("Le mot de passe doit contenir au moins un caractère spécial")
        if not requirements["common"]: errors.append("Le mot de passe est trop commun ou facile à deviner")
    return len(errors) == 0, errors

# ---------------- Routes ----------------

@register_bp.route('/check_password', methods=['POST'])
def check_password():
    password = request.form.get('password', '')
    is_valid, errors = validate_password_strength(password)
    analysis = analyze_password(password)
    return jsonify({
        'valid': is_valid,
        'errors': errors,
        'score': analysis['score'],
        'feedback': analysis['feedback'],
        'crack_time': analysis['crack_time']
    })

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            firstname = request.form['user_firstname'].strip()
            lastname = request.form['user_lastname'].strip()
            email = request.form['user_email'].strip().lower()
            password = request.form['user_password']
            phone = (request.form.get('user_phone') or '').strip() or None

            errors = []
            if not re.match(r'^[a-zA-ZÀ-ÿ\s-]{2,50}$', firstname):
                errors.append("Prénom invalide (2-50 lettres, accents autorisés)")
            if not re.match(r'^[a-zA-ZÀ-ÿ\s-]{2,50}$', lastname):
                errors.append("Nom invalide (2-50 lettres, accents autorisés)")
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("Format d'email invalide")
            if len(password) < 12:
                errors.append("Le mot de passe doit contenir au moins 12 caractères")
            elif not any(c.isupper() for c in password):
                errors.append("Le mot de passe doit contenir au moins une majuscule")
            if phone and not re.match(r'^\+?[\d\s-]{7,15}$', phone):
                errors.append("Format de téléphone invalide (ex: +33 6 12 34 56 78)")

            if errors:
                for e in errors: flash(e, 'danger')
                return redirect(url_for('register_bp.register'))

            if not request.form.get('consent_data'):
                flash("Vous devez accepter la collecte de vos données personnelles pour vous inscrire.", 'danger')
                return redirect(url_for('register_bp.register'))

            if User.query.filter_by(user_email=email).first():
                flash("Un compte existe déjà avec cet email", 'danger')
                return redirect(url_for('register_bp.register'))

            new_user = User(
                user_firstname=firstname,
                user_lastname=lastname,
                user_email=email,
                user_phone=phone
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash("Votre compte a été créé avec succès !", 'success')
            return redirect(url_for('login_bp.login'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur inscription: {str(e)}", exc_info=True)
            flash("Une erreur technique est survenue. Veuillez réessayer.", 'danger')
            return redirect(url_for('register_bp.register'))

    return render_template('register.html')
