from flask import Blueprint, render_template, session, redirect, url_for, flash
from models import db
from models.user_model import User
from models.order_model import Order
from models.order_details_model import OrderDetail

# Déclaration du Blueprint
account_bp = Blueprint('account_bp', __name__)

@account_bp.route('/account')
def user_dashboard():
    """Affiche l'espace personnel de l'utilisateur."""
    user_id = session.get('user_id')
    if not user_id:
        flash("Veuillez vous connecter pour accéder à votre espace personnel.", "warning")
        return redirect(url_for('login_bp.login'))

    user = User.query.get(user_id)
    user_orders = Order.query.filter_by(user_id=user_id, payment_status="paid").order_by(Order.order_date.desc()).all()

    return render_template('account.html', user=user, orders=user_orders)


@account_bp.route('/account/order/<int:order_id>')
def order_details(order_id):
    """Affiche les détails d'une commande spécifique."""
    user_id = session.get('user_id')
    if not user_id:
        flash("Veuillez vous connecter pour voir vos commandes.", "warning")
        return redirect(url_for('login_bp.login'))

    order = Order.query.get(order_id)
    if not order or order.user_id != user_id:
        flash("Commande introuvable ou accès interdit.", "danger")
        return redirect(url_for('account_bp.user_dashboard'))

    return render_template('order_details.html', order=order)
