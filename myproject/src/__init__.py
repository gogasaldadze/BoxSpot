from flask import Flask
from src.config import Config
from src.extensions import db
from src.views import main_blueprint,products_blueprint

BLUEPRINTS = [main_blueprint,products_blueprint]



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)

    return app





def register_extensions(app):
    db.init_app(app)

def register_blueprints(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
    

def register_commands(app):
    pass