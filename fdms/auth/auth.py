import traceback
from flask import current_app as app
from flask import abort, request, Response
import fdms
from pprint import pformat
from functools import wraps

class AuthService(fdms.RequestHandler):
    def __init__(self):
        super().__init__()
        self.authenticate()


    def cookie_auth(self, options):
        http_username = request.authorization["username"]
        tmp = http_username.split("|")
        tenant = tmp[0]
        user_id = tmp[1]
        password = request.authorization["password"]

        users = [u for u in app.config["DMS_STATIC_USERS"] if u["tenant_id"] == tenant and u["user_id"] == user_id and u["password"] == password]
        return users[0] if len(users) > 0 else None

    def set_cookie(self, options):
        resp.set_cookie('userID', user)

    def static_auth(self, options):
        http_username = request.authorization["username"]
        tmp = http_username.split("|")
        tenant = tmp[0]
        user_id = tmp[1]
        password = request.authorization["password"]

        users = [u for u in app.config["DMS_STATIC_USERS"] if u["tenant_id"] == tenant and u["user_id"] == user_id and u["password"] == password]
        return users[0] if len(users) > 0 else None

    def authenticate(self):

        try:
            self.logger.debug("Trying authentication")
            print(pformat(self.logger))
            for method in app.config["AUTHENTICATION"]:
                func = getattr(self, "{}_auth".format(method["type"]))
                user = func(method)
                if user: 
                    context = fdms.Context(user)
                    self.set_request_attr("context", context)
                    self.set_context(context)
                    if (method.get("callback")):
                        func = getattr(self, method.get("callback"))
                        func(context)

                    self.logger.debug("Authenticated (%s) %s", method["type"], str(context))
                    break
            
            if not context:
                self.logger.debug("Authenticated failed")
                
            return context
        except:
            traceback.print_exc()
            abort(401, "Cannot authenticate request")
            return None


def is_fdms_admin(func):
    """Decorator for app admin authorized views"""
    @wraps(func)
    def admin_wrapper(**args):
        print("a")
        """Wrapper"""
        service = AuthService()
        if service.context.is_fdms_admin():
            return func(**args)
        else:
            abort(403)
            return None
    return admin_wrapper

def is_logged_in(func):
    """Decorator for app logged_in authorized views"""
    @wraps(func)
    def logged_in_wrapper():
        """Wrapper"""
        AuthService()
        return func()
    return logged_in_wrapper

def custom_401(error):
    """Not authorized response"""
    print(error)
    return Response('Access denied'
                    , 401
                    , {'WWW-Authenticate':'Basic realm="Login Required"'})