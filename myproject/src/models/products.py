from flask_login import UserMixin

from src.extensions import db


class Prod(db.Model,UserMixin):
    
    __tablename__ = "products"

    id =db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    category = db.Column(db.String, nullable = False)
    price = db.Column(db.Integer, nullable = False)
    image = db.Column(db.String)