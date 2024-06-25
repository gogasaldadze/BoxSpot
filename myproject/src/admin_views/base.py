from flask_admin.contrib.sqla import ModelView

class SecureModelView(ModelView):
    def is_accessible(self):
        return 