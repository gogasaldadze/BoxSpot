from flask import render_template, Blueprint, flash, redirect, url_for, request
from flask_login import login_user, logout_user
from os import path

from src.config import Config
from src.views.auth.forms import RegisterForm, LoginForm, ResetPasswordForm, ResetPasswordRequestForm
from src.models.user import User
from src.extensions import db
from src.utilis import send_mail, create_key, confirm_key

TEMPLATES_FOLDER = path.join(Config.BASE_DIRECTORY, "templates", "auth")
auth_blueprint = Blueprint("auth", __name__, template_folder=TEMPLATES_FOLDER)

@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data, phone = form.phone.data)
        db.session.add(user)
        db.session.commit()

        activation_key = create_key(form.email.data)
        activation_link = url_for('auth.activate_account', activation_key=activation_key, _external=True)
        html = render_template("_activation.html", activation_link=activation_link)
        send_mail("მომხმარებლის გააქტიურება", html, [form.email.data])

        flash("თქვენ წარმატებით გაიარეთ რეგისტრაცია! გთხოვთ შეამოწმოთ ელ-ფოსტა ექაუნთის გასააქტიურებლად.")
        return redirect(url_for('auth.login'))  
    return render_template("register.html", form=form)

@auth_blueprint.route("/activate_account/<activation_key>")
def activate_account(activation_key):
    email = confirm_key(activation_key)
    if not email:
        flash("აქტივაციის ლინკს გაუვიდა ვადა.")
        return redirect(url_for("auth.login"))
    
    user = User.query.filter_by(email=email).first()
    if user:
        if not user.active:
            user.active = True
            db.session.commit()
            flash("თქვენი ექაუნთი გააქტიურდა, გთხოვთ გაიაროთ ავტორიზაცია.")
        else:
            flash("თქვენი ექაუნთი უკვე აქტიურია..")
    else:
        flash("მომხმარებელი ვერ მოიძებნა")
    
    return redirect(url_for("auth.login"))

@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("მომხმარებელი ვერ მოიძებნა")
            return redirect(url_for("auth.login"))
        
        if not user.active:
            flash("თქვენი ექაუნთი არ არის აქტიური, გთხოვთ შეამოწმოთ ელ-ფოსტა ექაუნთის გასააქტიურებლად.")
            return redirect(url_for("auth.login"))
        
        if not user.check_password(form.password.data):
            flash("პაროლი არასწორია, სცადეთ ხელახლა.")
            return redirect(url_for("auth.login"))
        
        login_user(user)
        next_page = request.args.get("next")
        return redirect(next_page or "/")
    
    return render_template("login.html", form=form)

@auth_blueprint.route("/logout")
def logout():
    logout_user()
    flash("თქვენ გამოხვედით")
    return redirect("/")



@auth_blueprint.route("/reset_password", methods=["GET", "POST"])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            reset_key = create_key(form.email.data)
            reset_link = url_for('auth.reset_password', reset_key=reset_key, _external=True)
            html = render_template("reset_password_email.html", reset_link=reset_link)
            send_mail("Password Reset Request", html, [form.email.data])
        
        flash("თუ ეს ელ.ფოსტა რეგისტრირებული იყო, გაიგებთ პაროლის აღდგენის ლინკს.")
        return redirect(url_for('auth.login'))

    return render_template("reset_password_request.html", form=form)


@auth_blueprint.route("/reset_password/<reset_key>", methods=["GET", "POST"])
def reset_password(reset_key):
    email = confirm_key(reset_key)
    if not email:
        flash("პაროლის აღდგენის ლინკს გაუვიდა ვადა.")
        return redirect(url_for("auth.login"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = form.password.data  # Make sure to hash the password
            db.session.commit()
            flash("თქვენი პაროლი წარმატებით შეიცვალა. ახლა შეგიძლიათ შეხვიდეთ.")
            return redirect(url_for('auth.login'))

    return render_template("reset_password.html", form=form)
