from flask import current_app as app
from flask import abort, request, Response
import fdms.utils as utils


def get_user():
    """Returns the logged in user"""
    return utils.get_request_attr("user")


def admin(func):
    """Decorator for app admin authorized views"""
    def wrapper():
        """Wrapper"""
        try:
            http_username = request.authorization["username"]
            tmp = http_username.split("|")
            tenant = tmp[0]
            login = tmp[1]
            password = request.authorization["password"]
            print(tenant, login, password)

            users = [ u for u in app.config["DMS_STATIC_USERS"] if u["tenant"] == tenant and u["login"] == login and u["password"] == password ]
            print(users[0])
            utils.set_request_attr("user", users[0])

        except Exception as e:
            import traceback
            traceback.print_exc()
            abort(401)

        return func()

    return wrapper

def custom_401(error):
    """Not authorized response"""
    return Response('<Why access is denied string goes here...>'
                    , 401
                    , {'WWW-Authenticate':'Basic realm="Login Required"'})