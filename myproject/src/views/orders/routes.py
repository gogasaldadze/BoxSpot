from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from src.config import Config
from src.models import Order  
import os   

TEMPLATES_FOLDER = os.path.join(Config.BASE_DIRECTORY, "templates", "order")
order_blueprint = Blueprint("order_blueprint", __name__, template_folder=TEMPLATES_FOLDER)

@order_blueprint.route('/my_order/<int:user_id>')
@login_required
def my_order(user_id):
    if current_user.id != user_id:
        flash("You do not have permission to view this order.")
        return redirect(url_for('products.view_cart'))

    orders = Order.query.filter_by(user_id=user_id).all()
    
    return render_template('my_order.html', orders=orders)
