from . import db

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)

    # backref depuis Book (voir book_model)
    books = db.relationship('Book', back_populates='category', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.category_name}>"
