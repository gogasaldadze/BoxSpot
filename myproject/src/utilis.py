from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from src.extensions import mail
from src.config import Config

def send_mail(subject,text,recipients):
    message = Message(subject = subject, html = text , recipients = recipients, sender = Config.MAIL_SENDER)
    mail.send(message)


def create_key(email):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    key = serializer.dumps(email, salt =Config.SERIALIZER_SALT)

    print(key)
    return key

def confirm_key(activation_key):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(activation_key, salt=Config.SERIALIZER_SALT, max_age = 300)
        return True
    except:
        return False
    

