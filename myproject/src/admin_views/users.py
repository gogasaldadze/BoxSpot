from src.admin_views.base import SecureModelView

class UserView(SecureModelView):

    can_view_details = True
    can_export = True