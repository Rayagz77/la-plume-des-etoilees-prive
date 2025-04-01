import stripe
from flask import Blueprint, request, jsonify, url_for, flash, redirect, render_template  # Ajout de render_template
from controllers.access_management import admin_required, user_required, guest_required

from config import STRIPE_SECRET_KEY  # Récupération de la clé Stripe
from models import db, Order  # Import des modèles nécessaires

stripe.api_key = STRIPE_SECRET_KEY

payement_bp = Blueprint('payement_bp', __name__)

@payement_bp.route('/create-checkout-session/<int:order_id>', methods=['GET', 'POST'])
def create_checkout_session(order_id):
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
            'product_data': {
                'name': f'Commande {order.order_id}',
            },
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

        # ✅ Si l’appel vient du navigateur (pas Ajax), on redirige directement
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({'url': session_stripe.url})
        else:
            return redirect(session_stripe.url)

    except Exception as e:
        flash("Erreur lors de la création de la session de paiement.", "danger")
        return redirect(url_for('cart_bp.view_cart'))


@payement_bp.route('/payment-success/<int:order_id>')
def payment_success(order_id):
    """Gère la confirmation de paiement et propose des options de redirection."""
    order = Order.query.get(order_id)
    if not order:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('home'))

    # ✅ Mettre à jour le statut de paiement
    order.payment_status = "paid"
    db.session.commit()

    # ✅ Stocker le numéro de commande pour affichage
    flash(f"🎉 Paiement validé ! Votre commande n°{order.order_id} a été confirmée.", "success")

    # ✅ Proposer une redirection après paiement
    return render_template("payment_success.html", order=order)

@payement_bp.route('/payment-failed/<int:order_id>')
def payment_failed(order_id):
    """Gère les échecs de paiement."""
    order = Order.query.get(order_id)
    if not order:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('home'))

    order.payment_status = "failed"
    db.session.commit()
    flash("Le paiement a échoué. Veuillez réessayer.", "danger")

    return redirect(url_for('cart_bp.view_cart'))
