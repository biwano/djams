""" Various utils """
import uuid
from flask import request, abort
from passlib.context import CryptContext
from fdms.services import TENANT_ACES

PASSWORD_CONTEXT = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=300
)

def encrypt_password(password):
    return PASSWORD_CONTEXT.encrypt(password)

def check_encrypted_password(password, hashed):
    return PASSWORD_CONTEXT.verify(password, hashed)

def ensure_request_attr_container():
    if (not hasattr(request, "flaskdms")):
        setattr(request, "flaskdms", {})

def set_request_attr(key, value):
    ensure_request_attr_container()
    request.flaskdms[key] = value

def get_request_attr(key):
    ensure_request_attr_container()
    return request.flaskdms.get(key)

def get_user():
    """Returns the logged in user"""
    return get_request_attr("user")

def userIsFDMSAdmin():
    return get_user()["isFDMSAdmin"]

def get_request_tenant_id():
    tenant_id = get_request_attr("request_tenant_id")
    if not tenant_id:
        user = get_user()
        tenant_id = user["tenant_id"]
        wanted_tenant_id = request.args.get('tenant_id')
        if wanted_tenant_id:
            if userIsFDMSAdmin():
                tenant_id = wanted_tenant_id
            elif wanted_tenant_id != user["tenant_id"]:
                abort(403)
        set_request_attr("request_tenant_id", tenant_id)

    return tenant_id

def get_request_schema_id():
    schema_id = get_request_attr("request_schema_id")
    if not schema_id:
        schema_id = request.args.get('schema_id_id')
    return schema_id

def get_request_acls():
    if userIsFDMSAdmin():
        return TENANT_ACES
    else:
        return ["user:" + get_user()["login"]]

def get_uuid():
    return uuid.uuid4().hex
