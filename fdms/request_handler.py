""" Various utils """
import uuid
from flask import request, abort, jsonify
from passlib.context import CryptContext
import logging

PASSWORD_CONTEXT = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=300
)
class RequestHandler(object):
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.set_context(self.get_request_attr("context"))


    def set_context(self, context):
        self.context = context

    def encrypt_password(self, password):
        return PASSWORD_CONTEXT.encrypt(password)

    def check_encrypted_password(self, password, hashed):
        return PASSWORD_CONTEXT.verify(password, hashed)

    def ensure_request_attr_container(self):
        if (not hasattr(request, "flaskdms")):
            setattr(request, "flaskdms", {})

    def set_request_attr(self, key, value):
        self.ensure_request_attr_container()
        request.flaskdms[key] = value

    def get_request_attr(self, key):
        self.ensure_request_attr_container()
        return request.flaskdms.get(key)

    def get_request_tenant_id(self):
        tenant_id = self.get_request_attr("request_tenant_id")
        if not tenant_id:
            user = self.context.user
            tenant_id = user["tenant_id"]
            wanted_tenant_id = request.args.get('tenant_id')
            if wanted_tenant_id:
                if self.userIsFdmsAdmin():
                    tenant_id = wanted_tenant_id
                elif wanted_tenant_id != user["tenant_id"]:
                    abort(403)
            self.set_request_attr("request_tenant_id", tenant_id)

        return tenant_id

    def get_request_schema_id(self):
        schema_id = self.get_request_attr("request_schema_id")
        if not schema_id:
            schema_id = request.args.get('schema_id_id')
        return schema_id

    def get_body(self):
        return request.json

    def get_uuid(self):
        return uuid.uuid4().hex

    def send(self, data):
        return jsonify(data)

    def send_success(self, data):
        return self.send({"result": "ok"})
