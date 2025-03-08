import os
from dotenv import load_dotenv

# Charger les variables depuis le fichier .env
load_dotenv()

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'ta_clé_secrète')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'ta_clé_publique')
