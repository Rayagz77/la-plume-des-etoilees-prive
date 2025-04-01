from .import db

class Category(db.Model):
    __tablename__ = 'Category'  # Nom exact de la table en base de données
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)  # Ajout d'unicité pour éviter les doublons

    def __repr__(self):
        return f"<Category {self.category_name}>"
