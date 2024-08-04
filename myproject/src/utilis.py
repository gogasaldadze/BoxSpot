from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import os 

from src.extensions import mail
from src.config import Config

def send_mail(subject, html, recipients):
    message = Message(subject=subject, html=html, recipients=recipients, sender=Config.MAIL_SENDER)
    mail.send(message)

def create_key(email):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    key = serializer.dumps(email, salt=Config.SERIALIZER_SALT)
    return key

def confirm_key(activation_key):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(activation_key, salt=Config.SERIALIZER_SALT, max_age=300)
        return email
    except:
        return False

from flask_mail import Message

def send_invoice_email(recipient_email, invoice_path):
    with open(invoice_path, 'rb') as pdf:
        msg = Message(
            subject="Your Invoice from Boxspot",
            sender=Config.MAIL_SENDER,
            recipients=[recipient_email]
        )
        msg.body = "Dear Customer,\n\nPlease find attached your invoice for the recent order.\n\nThank you for your purchase!"
        msg.attach(
            filename=os.path.basename(invoice_path),
            content_type='application/pdf',
            data=pdf.read()
        )
    
    try:
        mail.send(msg)
        print(f"Invoice sent to {recipient_email}.")
    except Exception as e:
        print(f"Error sending invoice email: {e}")
