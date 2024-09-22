from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from src.extensions import db

class User(db.Model,UserMixin):
    
    __tablename__ = "users"

    id =db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String, nullable = False, unique = True)
    username = db.Column(db.String, nullable = False)
    _password = db.Column(db.String, nullable = False)
    role = db.Column(db.String, default = 'member')
    phone = db.Column(db.Integer, nullable = False)

    active = db.Column(db.Boolean, default = False)
    



    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self.password, password)


    @property
    def is_admin(self):
        return self.role == 'admin'




    