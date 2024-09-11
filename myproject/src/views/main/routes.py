from flask import render_template, Blueprint
from os import path
from src.models import Prod
from src.config import Config

TEMPLATES_FOLDER = path.join(Config.BASE_DIRECTORY, "templates", "main")
main_blueprint = Blueprint("main", __name__, template_folder=TEMPLATES_FOLDER)


@main_blueprint.route("/home", methods=["GET", "POST"])
def home():
    # Retrieve all products
    all_products = Prod.query.all()
    
    # Filter products by category 'offer'
    offer_products = [p for p in all_products if p.category == 'offer']

    return render_template("home.html", Prod=all_products, offer_products=offer_products)

@main_blueprint.route("/", methods=["GET"])
def index():
    # Retrieve all products
    all_products = Prod.query.all()
    
    # Filter products by category 'offer'
    offer_products = [p for p in all_products if p.category == 'offer']

    return render_template("home.html", Prod=all_products, offer_products=offer_products)


@main_blueprint.route("/contact",methods = ["GET"])
def contact():
    return render_template("contact.html")

@main_blueprint.route('/conditions', methods =["GET"])
def conditions():
    return render_template("conditions.html")