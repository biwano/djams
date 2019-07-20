""" flaskdms configuration file """
CONFIG = {
    "DMS_STATIC_USERS": [{
        "tenant": "*",
        "login": "admin",
        "password": "admin"
    }],
    "SQLALCHEMY_DATABASE_URI":"sqlite:////tmp/fdms.db"
}
