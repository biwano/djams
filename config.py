from fdms import CONFIG

CONFIG.update({
    "LOGGING" : {
        "SchemaService": {"level": "INFO"},
        "DocumentService": {"level": "INFO"},
        "EsService": {"level": "INFO"},
        "FlaskEs": {"level": "INFO"},
        "AuthService": {"level": "DEBUG"},
    }
})
