from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, RadioField, DateField, SelectField, TextAreaField, SubmitField, IntegerField,EmailField
from wtforms.validators import DataRequired, equal_to, length, ValidationError,Email
from string import ascii_uppercase, ascii_lowercase, digits, punctuation



class RegisterForm(FlaskForm):
    email = EmailField("ელექტორნული ფოსტა",validators = [DataRequired(),Email()])
    username = StringField("მომხმარებელის სახელი", validators=[DataRequired(),])
    password = PasswordField("პაროლო", validators=[DataRequired(),length(min=8, max=64, message="პაროლი უნდა იყოს მინიმუმ 8 სიმბოლო")])
    repeat_password = PasswordField("გაიმეორეთ პაროლი", validators=[DataRequired(),equal_to("password", message="პაროლები არ ემთხვევა")])
    submit = SubmitField('რეგისტრაცია')


    def validate_email(self,field):
        pass

    def validate_username(self,field):
        pass

    def validate_password(self,field):
        pass