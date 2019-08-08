""" flaskdms configuration file """
CONFIG = {
    "DMS_STATIC_USERS": [{
        "tenant_id": "*",
        "login": "admin",
        "password": "admin"
    }],
    "SQLALCHEMY_DATABASE_URI": "sqlite:////tmp/fdms.db",
    "ELASTICSEARCH": {"hosts": ["localhost"]},
    "AUTHENTICATION": [{"type": "static"}],
    "LOGGING" : {
        "SchemaService": {"level": "INFO"},
        "DocumentService": {"level": "INFO"},
        "EsService": {"level": "INFO"},
        "FlaskEs": {"level": "INFO"},
        "AuthService": {"level": "INFO"},
    }
}