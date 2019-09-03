import flask
from flask_cors import CORS
#from flask_session import Session
import fdms
import logging
from config import CONFIG


# setting up logging
logformat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=logformat)

for clazz in fdms.CONFIG.get("LOGGING"):
    logger = logging.getLogger(clazz)
    level = fdms.CONFIG.get("LOGGING").get(clazz).get("level")
    logger.setLevel(getattr(logging, level))
    #handler = logging.StreamHandler()
    #formatter = logging.Formatter(logformat)
    #handler.setFormatter(formatter)
    #logger.addHandler(handler)


# Creating app
app = flask.Flask(__name__)
app.config.update(CONFIG)

# Initializing cors
CORS(app, supports_credentials=True)

# Initializing session
#SESSION_TYPE = 'filesystem'
#Session(app)

# Initializing elasticsearch
fdms.services.FlaskEs(app)

# initializing cache
fdms.services.FlaskCache(app)

# setting up views
@app.errorhandler(401)
def custom_401(error):
    return fdms.auth.custom_401(error)

# Tenants
@app.route('/tenants', methods=["POST"])
@fdms.auth.is_fdms_admin
def create_tenant():
    return fdms.views.TenantsView().create()


@app.route('/tenants/<tenant_id>', methods=["DELETE"])
@fdms.auth.is_fdms_admin
def delete_tenant(tenant_id):
    return fdms.views.TenantsView().delete(tenant_id)

# Search
@app.route('/<tenant_id>/search', methods=["GET"])
@fdms.auth.is_logged_in
def search(tenant_id):
    return fdms.views.DocumentsView().search()


@app.route('/<tenant_id>/filter', methods=["GET"])
@fdms.auth.is_logged_in
def filter(tenant_id):
    return fdms.views.DocumentsView().filter()

# documents
"""
@app.route('/documents', methods=["POST"])
@fdms.auth.is_logged_in
def create():
    return fdms.views.DocumentsView().create()
"""

@app.route('/<tenant_id>/documents/', defaults={'doc': ''})
@app.route('/<tenant_id>/documents/<path:doc>', methods=["GET"])
@fdms.auth.is_logged_in
def get(tenant_id, doc):
    return fdms.views.DocumentsView().get(doc)

@app.route('/auth', methods=["GET"])
@fdms.auth.is_logged_in
def get_user():
    return fdms.views.AuthView().get_logged_in_user()
