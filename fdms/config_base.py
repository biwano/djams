""" flaskdms configuration file """
CONFIG = {
    "DMS_STATIC_USERS": [{
        "tenant_id": "*",
        "user_id": "admin",
        "password": "admin"
    }],
    "SQLALCHEMY_DATABASE_URI": "sqlite:////tmp/fdms.db",
    "ELASTICSEARCH": {"hosts": ["localhost"]},
    "AUTHENTICATION": [{"type": "static", "on_sucess": "set_cookie"}],
    "LOGGING" : {
        "SchemaService": {"level": "INFO"},
        "DocumentService": {"level": "INFO"},
        "EsService": {"level": "INFO"},
        "FlaskEs": {"level": "INFO"},
        "AuthService": {"level": "INFO"},
    }
}