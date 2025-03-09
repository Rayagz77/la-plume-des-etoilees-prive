import os
from dotenv import load_dotenv

# Charger les variables depuis le fichier .env
load_dotenv()

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'ta_clé_secrète')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'ta_clé_publique')
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
