""" Tenant views implementation """
import fdms

class AuthView(fdms.RequestHandler):
    def __init__(self):
        super().__init__()

    def get_logged_in_user(self):
        """Returns logged in user"""
        return self.context.user
