import fdms.auth as auth

def create():
    """Creates a new realm"""
    return 'Hello ' + auth.get_user()["login"]