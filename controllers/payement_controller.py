import stripe
from flask import Blueprint, request, jsonify, url_for, flash, redirect
from config import STRIPE_SECRET_KEY # Remonte d'un niveau pour accéder à config.py
from models import db, Order # Remonte d'un niveau pour accéder à models

stripe.api_key = STRIPE_SECRET_KEY

payement_bp = Blueprint('payement_bp', __name__)

@payement_bp.route('/create-checkout-session/<int:order_id>', methods=['POST'])
def create_checkout_session(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Commande introuvable'}), 404

    line_items = [{
        'price_data': {
            'currency': 'eur',
            'product_data': {
                'name': f'Commande {order.order_id}',
            },
            'unit_amount': int(order.total_price * 100),
        },
        'quantity': 1,
    }]

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payement_bp.payment_success', order_id=order_id, _external=True),
            cancel_url=url_for('payement_bp.payment_failed', order_id=order_id, _external=True),
        )
        return jsonify({'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payement_bp.route('/payment-success/<int:order_id>')
def payment_success(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('home'))
    order.payment_status = "paid"
    db.session.commit()
    flash("Paiement réussi ! Votre livre vous a été envoyé par email.", "success")
    return redirect(url_for('cart_bp.order_confirmation', order_id=order_id))

@payement_bp.route('/payment-failed/<int:order_id>')
def payment_failed(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('home'))
    order.payment_status = "failed"
    db.session.commit()
    flash("Le paiement a échoué. Veuillez réessayer.", "danger")
    return redirect(url_for('cart_bp.view_cart'))
