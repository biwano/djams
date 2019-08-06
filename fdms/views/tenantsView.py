""" Tenant views implementation """
from flask import request
from fdms import services

def create():
    """Creates a new realm"""
    body = request.json
    tenant_id = body["tenant_id"]
    drop = body.get("drop")
    services.TenantService(tenant_id).create(drop)

    return body
