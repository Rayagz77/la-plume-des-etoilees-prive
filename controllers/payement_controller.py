import os
from flask import Blueprint, request, jsonify, url_for, flash, redirect, render_template
from models import db
from models.order_model import Order

try:
    import stripe
except Exception:
    stripe = None

SECRET = os.getenv("STRIPE_SECRET_KEY")
if stripe and SECRET:
    stripe.api_key = SECRET

payement_bp = Blueprint('payement_bp', __name__)

@payement_bp.route('/create-checkout-session/<int:order_id>', methods=['GET', 'POST'])
def create_checkout_session(order_id):
    if not stripe or not SECRET:
        flash("Paiement indisponible (Stripe non configuré).", "danger")
        return redirect(url_for('cart_bp.view_cart'))

    order = Order.query.get(order_id)
    if not order:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('home'))

    if order.payment_status == "paid":
        flash("Cette commande a déjà été payée.", "info")
        return redirect(url_for('home'))

    line_items = [{
        'price_data': {
            'currency': 'eur',
            'product_data': {'name': f'Commande {order.order_id}'},
            'unit_amount': int(order.total_price * 100),
        },
        'quantity': 1,
    }]

    try:
        session_stripe = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payement_bp.payment_success', order_id=order_id, _external=True),
            cancel_url=url_for('payement_bp.payment_failed', order_id=order_id, _external=True),
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({'url': session_stripe.url})
        return redirect(session_stripe.url)

    except Exception:
        flash("Erreur lors de la création de la session de paiement.", "danger")
        return redirect(url_for('cart_bp.view_cart'))


@payement_bp.route('/payment-success/<int:order_id>')
def payment_success(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('home'))

    order.payment_status = "paid"
    db.session.commit()
    flash(f"🎉 Paiement validé ! Votre commande n°{order.order_id} a été confirmée.", "success")
    return render_template("payment_success.html", order=order)

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
