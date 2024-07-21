from flask import Flask

from src.admin_views import SecureModelView, ProdView,UserView
from src.config import Config
from src.extensions import db, login_manager,admin, migrate
from src.views import main_blueprint,products_blueprint, auth_blueprint
from src.models import Prod, User
from src.commands import create_db , create_admin


BLUEPRINTS = [main_blueprint,products_blueprint, auth_blueprint]
COMMANDS =[create_db,create_admin ]



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)

    return app





def register_extensions(app):
    #db
    db.init_app(app)
    login_manager.init_app(app)

    #admin
    admin.init_app(app)
    admin.add_view(SecureModelView(User, db.session, name='Users'))
    admin.add_view(ProdView(Prod, db.session, name='Products'))
   
    #login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    #migrate
    migrate.init_app(app,db)



def register_blueprints(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
    

def register_commands(app):
    for command in COMMANDS:
        app.cli.add_command(command)