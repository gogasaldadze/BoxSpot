from os import path, environ
import os

class Config:
    BASE_DIRECTORY = path.abspath(path.dirname(__file__))
    UPLOAD_DIRECTORY = os.path.join(BASE_DIRECTORY, 'static', 'uploads')
    INVOICE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'invoices')
    SECRET_KEY = "myStrangeSecretKey34"
    SERIALIZER_SALT = "ABJARI123ekosistema"
    
    SQLALCHEMY_DATABASE_URI ="sqlite:///" + path.join(BASE_DIRECTORY,"Database.db")

    
    if environ.get("FLASK_ENV") == "production":
        pass
    else:
        MAIL_SENDER = "boxspot@info.ge"
        MAIL_SERVER = "sandbox.smtp.mailtrap.io"
        MAIL_PORT = 2525
        MAIL_USE_TLS = True
        MAIL_USE_SSL = False
        MAIL_USERNAME = "5609fde18d99c7"
        MAIL_PASSWORD = "69e0421b5b5368"
