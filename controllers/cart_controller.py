from flask import Blueprint, session, flash, redirect, url_for, render_template
from models import db, CartItem, Order, OrderDetail
from datetime import datetime

cart_bp = Blueprint('cart_bp', __name__)

@cart_bp.route('/add/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Veuillez vous connecter pour ajouter des articles au panier.", "warning")
        return redirect(url_for('login_bp.login'))

    existing_item = CartItem.query.filter_by(user_id=user_id, book_id=book_id).first()
    if existing_item:
        flash("Ce livre est déjà dans votre panier.", "info")
    else:
        new_item = CartItem(user_id=user_id, book_id=book_id)
        db.session.add(new_item)
        db.session.commit()
        flash("Livre ajouté au panier avec succès.", "success")
    
    return redirect(url_for('gallery'))

@cart_bp.route('/remove/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get(cart_item_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Article retiré du panier avec succès.", "success")
    return redirect(url_for('cart_bp.view_cart'))

@cart_bp.route('/', methods=['GET'])
def view_cart():
    user_id = session.get('user_id')
    if not user_id:
        flash("Veuillez vous connecter pour voir votre panier.", "warning")
        return redirect(url_for('login_bp.login'))

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total_price = sum(item.book.book_price for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@cart_bp.route('/validate', methods=['POST'])
def validate_cart():
    user_id = session.get('user_id')
    if not user_id:
        flash("Veuillez vous connecter pour valider votre panier.", "warning")
        return redirect(url_for('login_bp.login'))

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        flash("Votre panier est vide.", "info")
        return redirect(url_for('cart_bp.view_cart'))

    # Création d'une nouvelle commande
    order = Order(user_id=user_id, order_date=datetime.utcnow(), total_price=0)
    db.session.add(order)
    db.session.flush()

    # Création des détails de la commande
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

    # Mise à jour du total de la commande
    order.total_price = total_price

    # Suppression des articles du panier
    CartItem.query.filter_by(user_id=user_id).delete()

    db.session.commit()
    flash("Commande validée avec succès.", "success")
    return redirect(url_for('cart_bp.order_confirmation', order_id=order.order_id))

@cart_bp.route('/confirmation/<int:order_id>', methods=['GET'])
def order_confirmation(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('home'))

    return render_template('order_confirmation.html', order=order)

# Injecter le nombre d'articles dans le panier dans tous les templates
@cart_bp.context_processor
def inject_cart_count():
    user_id = session.get('user_id')
    cart_count = 0
    if user_id:
        cart_count = CartItem.query.filter_by(user_id=user_id).count()
    return {'cart_count': cart_count}
