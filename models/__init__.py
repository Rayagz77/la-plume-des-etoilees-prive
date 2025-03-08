from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importer les modèles
from .book_model import Book
from .category_model import Category
from .author_model import Author
from .cart_items_model import CartItem
from .order_model import Order, OrderDetail
from .user_model import User
