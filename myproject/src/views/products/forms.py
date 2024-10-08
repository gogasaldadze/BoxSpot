from flask_wtf import FlaskForm
from src.models.user import User
from wtforms.fields import StringField, PasswordField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Email, NumberRange
from wtforms import HiddenField
from string import ascii_uppercase, ascii_lowercase, digits, punctuation




class OrderForm(FlaskForm):
    name = StringField("მყიდველის სახელი", validators=[DataRequired()])
    id = IntegerField("საკადასტრო კოდი", validators=[DataRequired()])
    email = EmailField("ელექტრონული ფოსტა", validators=[DataRequired(), Email()])
    phone = IntegerField("ტელეფონის ნომერი", validators = [DataRequired()])
    submit = SubmitField('შეკვეთის გაფორმება')


    def validate_id(form, field):
        data = str(field.data)
        # print(len(data))
        if len(data) != 9 or not data.isdigit():
            raise ValidationError("საკადასტრო კოდი უნდა შეიცავდეს 9 ციფრს")
    
    def validate_phone(form,field):
        data = str(field.data)
        if len(data) != 9 or not data.isdigit():
            raise ValidationError("გთხოვთ შეიყვანოთ სწორი ნომერი")



class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Cart')


class UpdateCartForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    
class RemoveFromCartForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])