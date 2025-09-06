# controllers/stripe_hooks.py
import os
from flask import Blueprint, request
try:
    import stripe
except Exception:
    stripe = None

bp = Blueprint("stripe_hooks", __name__)

@bp.post("/webhook/stripe")
def stripe_webhook():
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not stripe or not endpoint_secret:
        return "Webhook off (stripe/secret missing)", 200

    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, endpoint_secret)
    except Exception:
        return "Bad signature", 400

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        # TODO: marquer la commande comme payée, envoyer e-mail, etc.

    return "", 200
