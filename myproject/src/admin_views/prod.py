from wtforms.fields import SelectField
from flask_admin.form import ImageUploadField


from src.admin_views.base import SecureModelView
from src.config import Config

class ProdView(SecureModelView):

    can_view_details = True
    can_export = True
 
    column_searchable_list = ['name', 'price']
    column_labels = {
        'name': 'სახელი',
        'price': 'ფასი',
        'description': 'აღწერა',
        'image': 'სურათი',
        'category':'კატეგორია'
    }
    column_editable_list = ['name', 'price', 'description' ]
    form_overrides = {
        'category': SelectField,
        'image': ImageUploadField
    }
    form_args = {'image':{'base_path':Config.UPLOAD_DIRECTORY},
                 'category':{'choices':['ყუთი','შესაფუთი ქაღალდი','აქსესუარები','offer']}
                 
                 }
    
    