from flask import Flask, render_template, request, session
from dotenv import load_dotenv
from flask_migrate import Migrate
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db
from models.book_model import Book
from models.category_model import Category
from models.author_model import Author
from models.cart_items_model import CartItem
from controllers.register_controller import register_bp
from controllers.auth_controller import login_bp
from controllers.admin_controller import admin_bp
from controllers.cart_controller import cart_bp  

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('SECRET_KEY')

    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(register_bp, url_prefix='/register')
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cart_bp, url_prefix='/cart')

    # Ajouter un processeur de contexte global pour injecter `cart_count`
    @app.context_processor
    def inject_cart_count():
        user_id = session.get('user_id')
        cart_count = 0
        if user_id:
            cart_count = CartItem.query.filter_by(user_id=user_id).count()
        return {'cart_count': cart_count}

    @app.route('/')
    def home():
        try:
            selected_category_id = request.args.get('category', type=int)
            page = request.args.get('page', 1, type=int)
            per_page = 9

            if selected_category_id:
                pagination = Book.query.filter_by(category_id=selected_category_id).paginate(page=page, per_page=per_page, error_out=False)
            else:
                pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)

            books = pagination.items
            categories = Category.query.all()

            return render_template('home.html', books=books, pagination=pagination, categories=categories, selected_category_id=selected_category_id)
        except Exception as e:
            print("Error:", e)
            return str(e)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
