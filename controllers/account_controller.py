# controllers/account_controller.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.orders_model import Orders  # adapte le chemin si ton modèle s'appelle autrement

account_bp = Blueprint("account_bp", __name__)

def _current_uid():
    # suivant ton modèle User: parfois c’est user_id, parfois id
    return getattr(current_user, "user_id", None) or getattr(current_user, "id", None)

@account_bp.get("/dashboard")
@login_required
def user_dashboard():
    uid = _current_uid()
    orders = []
    if uid:
        # tri du plus récent au plus ancien
        orders = Orders.query.filter_by(user_id=uid).order_by(Orders.order_date.desc()).all()
    # IMPORTANT: on passe 'user' au template, car account.html utilise {{ user.* }}
    return render_template("account.html", user=current_user, orders=orders)

@account_bp.get("/order/<int:order_id>")
@login_required
def order_details(order_id: int):
    uid = _current_uid()
    # sécurité: ne montrer que les commandes du user connecté
    order = Orders.query.filter_by(order_id=order_id, user_id=uid).first_or_404()
    return redirect(url_for("account_bp.user_dashboard"))
