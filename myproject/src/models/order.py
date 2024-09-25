from flask_login import UserMixin
from datetime import datetime

from src.extensions import db



class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Prod', backref=db.backref('orders', lazy=True))
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    @property
    def product_name(self):
        return self.product.name
    
    @property
    def user_name(self):
        return self.user.username
    
    @product_name.setter
    def product_name(self, value):
        self._product_name = value

    @user_name.setter
    def user_name(self,value):
       self._user_name = value 