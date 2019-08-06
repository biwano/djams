""" Tenant views implementation """
from flask import request, jsonify
from fdms import services
from fdms import utils

def search():
    """Creates a new realm"""
    tenant_id = utils.get_request_tenant_id()
    schema_id = utils.get_request_schema_id()
    acls = utils.get_request_attr("acls")
    docs = services.DocumentService(tenant_id, schema_id, acls).search()
    return jsonify(docs)
