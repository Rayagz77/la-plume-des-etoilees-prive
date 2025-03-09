from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importer les modèles dans l'ordre correct
from .user_model import User
from .book_model import Book
from .category_model import Category
from .author_model import Author
from .cart_items_model import CartItem
from .order_model import Order  # Order d'abord
from .order_details_model import OrderDetail  # OrderDetail ensuite
