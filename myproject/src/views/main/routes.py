from flask import render_template, Blueprint
from os import path

from src.config import Config

TEMPLATES_FOLDER = path.join(Config.BASE_DIRECTORY, "templates", "main")
main_blueprint = Blueprint("main", __name__, template_folder=TEMPLATES_FOLDER)


@main_blueprint.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@main_blueprint.route("/", methods=["GET"])
def index():
    return render_template("home.html")

@main_blueprint.route("/contact",methods = ["GET"])
def contact():
    return render_template("contact.html")