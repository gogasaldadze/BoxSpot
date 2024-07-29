from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_migrate import Migrate
from flask_mail import Mail
from src.admin_views.base import SecureAdminIndexView

db = SQLAlchemy()
admin = Admin(index_view=SecureAdminIndexView(),template_mode='bootstrap3')
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()