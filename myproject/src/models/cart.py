from datetime import datetime
from src.extensions import db

class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String, nullable=False)  # Store product name directly
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Prod', backref=db.backref('cart_items', lazy=True))
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
