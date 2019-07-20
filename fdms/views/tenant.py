import json
from fdms import auth, model, utils, Tenant, AlchemyEncoder
from flask import request, jsonify

def create():
    session = model.db.session
    """Creates a new realm"""
    body = request.json
    tenant = Tenant(uuid = utils.get_uuid(), id = body["id"], label = body["label"])
    session.add(tenant)
    session.commit()

    return json.dumps(tenant, cls=AlchemyEncoder)