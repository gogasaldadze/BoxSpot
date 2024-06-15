from os import path

class Config:
     BASE_DIRECTORY = path.abspath(path.dirname(__file__))
     SECRET_KEY = "myStrangeSecretKey34"
     SQLALCHEMY_DATABASE_URI ="sqlite:///" + path.join(BASE_DIRECTORY,"Database.db")
     