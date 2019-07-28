import json
from fdms import auth, model, utils, AlchemyEncoder, services
from flask import request, jsonify

def create():
    """Creates a new realm"""
    body = request.json
    tenant_id = body["tenant_id"]
    drop = body.get("drop")
    services.TenantService(tenant_id).create(drop)
    
    return body