from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Les imports de classes
from .user_model import User
from .book_model import Book
from .category_model import Category
from .author_model import Author
from .cart_items_model import CartItem
from .order_model import Order
from .order_details_model import OrderDetail
