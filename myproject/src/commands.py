from flask.cli import with_appcontext
import click
from src.extensions import db
from src.models import User
from werkzeug.security import generate_password_hash

#flask db migrate -m " " 
#flask db upgrade 


@click.command("create_db")
@with_appcontext
def create_db():
    click.echo("Creating DB")

    db.drop_all()
    db.create_all()

    click.echo("DB Created")


@click.command("create_admin")
@with_appcontext
def create_admin():
    click.echo("Creating admin user")

    
    user = User(
        email="saldadzegog@gmail.com",
        username="saldadzeadminer",
        password="Saldadzee!23",
        role="admin"
    )

    db.session.add(user)
    db.session.commit()

    click.echo("Admin user created")

    

