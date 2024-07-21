from flask_login import UserMixin

from src.extensions import db
# placeholder for importing basemodel

class User(db.Model,UserMixin):
    
    __tablename__ = "users"

    id =db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String, nullable = False, unique = True)
    username = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    role = db.Column(db.String, default = 'member')



    def is_admin(self):
        return self.role == 'admin'




    