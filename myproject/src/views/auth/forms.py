from flask_wtf import FlaskForm
from src.models.user import User
from wtforms.fields import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Email
from string import ascii_uppercase, ascii_lowercase, digits, punctuation

class RegisterForm(FlaskForm):
    email = EmailField("ელექტრონული ფოსტა", validators=[DataRequired(), Email()])
    username = StringField("მომხმარებლის სახელი", validators=[DataRequired()])
    password = PasswordField("პაროლი", validators=[DataRequired(), Length(min=8, max=64, message="პაროლი უნდა იყოს მინიმუმ 8 სიმბოლო")])
    repeat_password = PasswordField("გაიმეორეთ პაროლი", validators=[DataRequired(), EqualTo("password", message="პაროლები არ ემთხვევა")])
    submit = SubmitField('რეგისტრაცია')

    def validate_email(self, field):
        registered_email = User.query.filter_by(email=field.data).first()
        if registered_email:
            raise ValidationError("ელექტრონული ფოსტა უკვე რეგისტრირებულია")

    def validate_username(self, field):
        existing_user = User.query.filter_by(username=field.data).first()
        if existing_user:
            raise ValidationError("მომხმარებელი ამ სახელით უკვე არსებობს")

    def validate_password(self, field):
        contains_uppercase = any(char in ascii_uppercase for char in field.data)
        contains_lowercase = any(char in ascii_lowercase for char in field.data)
        contains_digits = any(char in digits for char in field.data)
        contains_punctuation = any(char in punctuation for char in field.data)

        if not contains_uppercase:
            raise ValidationError("პაროლი უნდა შეიცავდეს მინიმუმ 1 დიდ ასოს")
        if not contains_lowercase:
            raise ValidationError("პაროლი უნდა შეიცავდეს მინიმუმ 1 პატარა ასოს")
        if not contains_digits:
            raise ValidationError("პაროლი უნდა შეიცავდეს მინიმუმ 1 ციფრს")
        if not contains_punctuation:
            raise ValidationError("პაროლი უნდა შეიცავდეს მინიმუმ 1 სიმბოლოს")


class LoginForm(FlaskForm):
    username = StringField("მომხმარებლის სახელი", validators=[DataRequired()])
    password = PasswordField("პაროლი", validators=[DataRequired()])
    submit = SubmitField('შესვლა')