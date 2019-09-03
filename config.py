from fdms import CONFIG

CONFIG.update({
    "LOGGING" : {
        "SchemaService": {"level": "INFO"},
        "DocumentService": {"level": "INFO"},
        "EsService": {"level": "WARNING"},
        "FlaskEs": {"level": "INFO"},
        "AuthService": {"level": "INFO"},
        "elasticsearch": {"level": "WARNING"},
        "werkzeug": {"level": "WARNING"},
    },
    "CACHE": {
        'cache.type': 'memory'
    }
})
