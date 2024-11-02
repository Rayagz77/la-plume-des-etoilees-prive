from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user_model import User
from .book_model import Book
from .author_model import Author  
from .category_model import Category  
