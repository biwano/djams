import traceback
from flask import current_app as app
from flask import abort, request, Response
import fdms.utils as utils


def get_user():
    """Returns the logged in user"""
    return utils.get_user()

def authenticate():
    try:
        http_username = request.authorization["username"]
        tmp = http_username.split("|")
        tenant = tmp[0]
        login = tmp[1]
        password = request.authorization["password"]
        
        users = [ u for u in app.config["DMS_STATIC_USERS"] if u["tenant_id"] == tenant and u["login"] == login and u["password"] == password ]
        user = users[0]
        utils.set_request_attr("user", user)

        user["isFDMSAdmin"] = True if (user["tenant_id"] =="*") else False
        return get_user()
    except:
        traceback.print_exc()
        abort(401)
        return None

def admin(func):
    """Decorator for app admin authorized views"""
    def admin_wrapper():
        """Wrapper"""
        user = authenticate()
        if user and  user["tenant_id"] == "*":
            return func()
        else:
            abort(403)
            return None
    return admin_wrapper

def logged_in(func):
    """Decorator for app logged_in authorized views"""
    def logged_in_wrapper():
        """Wrapper"""
        authenticate()
        return func()
    return logged_in_wrapper

def custom_401(error):
    """Not authorized response"""
    return Response('Access denied'
                    , 401
                    , {'WWW-Authenticate':'Basic realm="Login Required"'})