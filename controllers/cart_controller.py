from flask import Blueprint, request, redirect, url_for, flash, session, render_template, jsonify
from controllers.access_management import user_required
from datetime import datetime
from models.user_model import User
from models import db
from models.order_model import Order
from models.order_details_model import OrderDetail
from models.cart_items_model import CartItem
from models.book_model import Book

# Déclaration du Blueprint
cart_bp = Blueprint('cart_bp', __name__)

@cart_bp.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    """Ajoute un livre au panier."""
    user_id = session.get('user_id')

    if not user_id:
        flash("Veuillez vous connecter pour sauvegarder votre panier et procéder au paiement.", "info")
        if 'cart_temp' not in session:
            session['cart_temp'] = []
        if book_id not in session['cart_temp']:
            session['cart_temp'].append(book_id)
            flash("Livre ajouté temporairement. Connectez-vous pour finaliser.", "success")
        else:
            flash("Ce livre est déjà dans votre panier temporaire.", "info")
        return redirect(url_for('gallery'))

    existing_item = CartItem.query.filter_by(user_id=user_id, book_id=book_id).first()
    if existing_item:
        flash("Ce livre est déjà dans votre panier.", "info")
    else:
        cart_item = CartItem(user_id=user_id, book_id=book_id)
        db.session.add(cart_item)
        db.session.commit()
        flash("Livre ajouté au panier.", "success")

    return redirect(url_for('gallery'))


@cart_bp.route('/view', methods=['GET'])
def view_cart():
    user_id = session.get('user_id')
    if not user_id:
        flash("Veuillez vous connecter pour voir votre panier.", "warning")
        return redirect(url_for('login_bp.login'))

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total_price = sum(item.book.book_price for item in cart_items) if cart_items else 0

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@cart_bp.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Veuillez vous connecter pour modifier votre panier.", "warning")
        return redirect(url_for('login_bp.login'))

    cart_item = CartItem.query.get(cart_item_id)
    if cart_item and cart_item.user_id == user_id:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Article retiré du panier.", "success")
    else:
        flash("Impossible de supprimer cet article.", "danger")

    return redirect(url_for('cart_bp.view_cart'))


@cart_bp.route('/checkout-summary', methods=['GET', 'POST'])
@user_required
def checkout_summary():
    user_id = session.get('user_id')
    if not user_id:
        flash("Veuillez vous connecter pour accéder au récapitulatif.", "warning")
        return redirect(url_for('login_bp.login'))

    user = User.query.get(user_id)
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total_price = sum(item.book.book_price for item in cart_items)
    tva = round(total_price * 0.2, 2)

    if request.method == 'POST':
        email = request.form.get('email') or user.user_email
        session['delivery_email'] = email

        # Création de la commande
        order = Order(user_id=user_id, order_date=datetime.utcnow(), total_price=0, payment_status="pending")
        db.session.add(order)
        db.session.flush()

        total_price = 0
        for item in cart_items:
            order_detail = OrderDetail(
                order_id=order.order_id,
                book_id=item.book_id,
                quantity=1,
                unit_price=item.book.book_price
            )
            db.session.add(order_detail)
            total_price += item.book.book_price

        order.total_price = total_price
        db.session.commit()

        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        return redirect(url_for('payement_bp.create_checkout_session', order_id=order.order_id))

    return render_template('checkout_summary.html', cart_items=cart_items, user=user, total_price=total_price, tva=tva)
