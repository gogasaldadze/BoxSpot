from flask import render_template, Blueprint, flash, redirect, url_for
from flask_login import login_user, logout_user
from os import path

from src.config import Config
from src.views.auth.forms import RegisterForm, LoginForm
from src.models.user import User
from src.extensions import db

TEMPLATES_FOLDER = path.join(Config.BASE_DIRECTORY, "templates", "auth")
auth_blueprint = Blueprint("auth", __name__, template_folder=TEMPLATES_FOLDER)

@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash ("მომხმარებელი ვერ მოიძებნა")
            return redirect(url_for("auth.login"))
        if user.password == form.password.data:
            login_user(user)
        else:
            flash ("პაროლი არასწორია")
        
    return render_template("login.html", form=form)

@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('auth.login'))  # Redirect to the login page after successful registration
    return render_template("register.html", form=form)

@auth_blueprint.route("/logout")
def logout():
    logout_user()
    flash("თქვენ დალოგაუთდით")
    return redirect("/")