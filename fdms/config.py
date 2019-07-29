""" flaskdms configuration file """
CONFIG = {
    "DMS_STATIC_USERS": [{
        "tenant": "*",
        "login": "admin",
        "password": "admin"
    }],
    "SQLALCHEMY_DATABASE_URI": "sqlite:////tmp/fdms.db",
    "ELASTICSEARCH_HOST": "loclahost:9200",
    "LOGGING" : {
    	"SchemaService": {"level": "INFO"},
    	"DocumentService": {"level": "DEBUG"},
    	"EsService": {"level": "DEBUG"},
    }
}
