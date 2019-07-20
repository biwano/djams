import flask
from flask_sqlalchemy import SQLAlchemy
import fdms

# Creating app
app = flask.Flask(__name__)
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
    return fdms.views.tenant.create()
