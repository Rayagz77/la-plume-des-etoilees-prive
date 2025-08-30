import os, stripe
from flask import Blueprint, request

bp = Blueprint("stripe_hooks", __name__)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@bp.post("/webhook/stripe")
def stripe_webhook():
    # En dev: autoriser l'endpoint même sans secret (no-op)
    if not WEBHOOK_SECRET:
        return "Webhook off (secret missing)", 200
    try:
        payload = request.get_data()
        sig = request.headers.get("Stripe-Signature", "")
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except Exception:
        return "Bad signature", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # TODO: marquer la commande comme payée
    return "", 200
