from flask import Blueprint, request, jsonify, redirect, url_for, flash, session, render_template
from datetime import datetime
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
        flash("Veuillez vous connecter pour ajouter un livre au panier.", "warning")
        return redirect(url_for('login_bp.login'))

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
    """Affiche le panier de l'utilisateur."""
    user_id = session.get('user_id')
    if not user_id:
        flash("Veuillez vous connecter pour voir votre panier.", "warning")
        return redirect(url_for('login_bp.login'))

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    total_price = sum(item.book.book_price for item in cart_items) if cart_items else 0

    if not cart_items:
        flash("Votre panier est vide.", "info")
    
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@cart_bp.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    """Supprime un article du panier."""
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

@cart_bp.route('/validate', methods=['POST'])
def validate_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Veuillez vous connecter pour valider votre panier."}), 403

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "Votre panier est vide."}), 400

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

    # Suppression du panier après validation
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # ✅ Retourne l'URL Stripe en JSON
    return jsonify({"redirect_url": url_for('payement_bp.create_checkout_session', order_id=order.order_id, _external=True)})
