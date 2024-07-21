from os import path
import os

class Config:
     BASE_DIRECTORY = path.abspath(path.dirname(__file__))
     UPLOAD_DIRECTORY = os.path.join(BASE_DIRECTORY, 'static','uploads')
     INVOICE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'invoices')
     SECRET_KEY = "myStrangeSecretKey34"
     SQLALCHEMY_DATABASE_URI ="sqlite:///" + path.join(BASE_DIRECTORY,"Database.db")
     