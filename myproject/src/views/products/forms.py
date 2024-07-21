from flask_wtf import FlaskForm
from src.models.user import User
from wtforms.fields import StringField, PasswordField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Email
from string import ascii_uppercase, ascii_lowercase, digits, punctuation



class OrderForm(FlaskForm):
    name = StringField("მყიდველის სახელი", validators=[DataRequired(),Length(min=3, max=44)])
    id = StringField("საკადასტრო კოდი", validators = [DataRequired(),Length(min=9,max=9)])
    email = EmailField("ელექტრონული ფოსტა",validators = [DataRequired(), Email()])
    quantity = IntegerField("რაოდენობა", validators = [DataRequired()])
    submit = SubmitField('შეკვეთის გაფორმება')



    def validate_id(self,field):
        if not field.data is digits:
            raise ValidationError("ს.კ არ უნდა შეიცავდეს ასოებს")
        
