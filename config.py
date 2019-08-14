from fdms import CONFIG

CONFIG.update({
    "LOGGING" : {
        "SchemaService": {"level": "DEBUG"},
        "DocumentService": {"level": "INFO"},
        "EsService": {"level": "DEBUG"},
        "FlaskEs": {"level": "INFO"},
        "AuthService": {"level": "DEBUG"},
    }
})
