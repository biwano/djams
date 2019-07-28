import flask
import fdms
import logging

# setting up logging
for clazz in fdms.CONFIG.get("LOGGING"):
    logger = logging.getLogger(clazz)
    level = fdms.CONFIG.get("LOGGING").get(clazz).get("level")
    logger.setLevel(getattr(logging, level))
    logger.addHandler(logging.StreamHandler())


# Creating app
app = flask.Flask(__name__)
app.config.setdefault('ELASTICSEARCH_HOST', 'localhost:9200')
app.config.setdefault('ELASTICSEARCH_HTTP_AUTH', None)
app.config.update(fdms.CONFIG)


# setting up sql model
fdms.db.app = app
fdms.db.init_app(app)

fdms.db.drop_all()
fdms.db.create_all()

# setting up views
@app.errorhandler(401)
def custom_401(error):
    return fdms.custom_401(error)

@app.route('/tenant', methods=["POST"])
@fdms.auth.admin
def create_realm():
    return fdms.views.tenantView.create()
