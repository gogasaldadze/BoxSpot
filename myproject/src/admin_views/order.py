from wtforms.fields import SelectField
from flask_admin.form import ImageUploadField

from src.admin_views.base import SecureModelView
from src.config import Config




class OrderView(SecureModelView):
    can_view_details = True
    can_export = True
    column_searchable_list = ['id', 'status', 'total_price', 'product.name']
    column_labels = {
        'product.name': 'Product',
        'user.username': 'User',
        'quantity': 'Quantity',
        'total_price': 'Total Price',
        'status': 'Status',
        'created_at': 'Created At'
    }
    column_editable_list = ['status']
    column_filters = ['status', 'created_at']
    form_choices = {
        'status': [
            ('Pending', 'Pending'),
            ('Shipped', 'Shipped'),
            ('Delivered', 'Delivered'),
            ('Cancelled', 'Cancelled')
        ]
    }

    column_list = ('id', 'product_name', 'user_name', 'quantity', 'total_price', 'status', 'created_at')

   
