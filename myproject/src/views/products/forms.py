from flask_wtf import FlaskForm
from src.models.user import User
from wtforms.fields import StringField, PasswordField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Email
from string import ascii_uppercase, ascii_lowercase, digits, punctuation




class OrderForm(FlaskForm):
    name = StringField("მყიდველის სახელი", validators=[DataRequired()])
    id = IntegerField("საკადასტრო კოდი", validators=[DataRequired()])
    email = EmailField("ელექტრონული ფოსტა", validators=[DataRequired(), Email()])
    quantity = IntegerField("რაოდენობა", validators=[DataRequired()])
    submit = SubmitField('შეკვეთის გაფორმება')


    def validate_id(form, field):
        data = str(field.data)
        # print(len(data))
        if len(data) != 9 or not data.isdigit():
            raise ValidationError("საკადასტრო კოდი უნდა შეიცავდეს 9 ციფრს")
    