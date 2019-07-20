from flask import Flask
import fdms

app = Flask(__name__)
app.config.update(fdms.CONFIG)


@app.errorhandler(401)
def custom_401(error):
	return fdms.custom_401(error)

@app.route('/realm')
@fdms.auth.admin
def create_realm():
    """Helloword."""
    return fdms.views.realm.create()
