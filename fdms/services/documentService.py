from .schemaService import SchemaService
from .. import model
from .constants import ROOT_DOCUMENT_UUID
from uuid import uuid4
import datetime
import json
import logging
from pprint import pformat
from .esService import es_service


class DocumentService():
    def __init__(self, tenant_id, schema_id):
        self.tenant_id = tenant_id
        self.schema_id = schema_id
        self.schema_service = SchemaService(tenant_id, schema_id)
        self.schema = self.schema_service.getProperties()
        self.logger = logging.getLogger(type(self).__name__)

    def __getPrimaryKey(self,doc):
        primary_key = self.schema_service.getPrimaryKey()
        key = {}
        for k in primary_key:
            key[k] = doc.get("k")

    def ensureBaseAcl(self, local_acl):
        # Local acls
        if local_acl is None:
            local_acl = []
        for ace in DocumentService.BASE_ACL:
            if ace not in local_acl:
                local_acl.append(ace)
        return local_acl

    def create(self, doc, parent_uuid=None, is_acl_inherited=True, local_acl=None):
        self.logger.debug("Creating document in schema %s/%s : %s", 
            self.tenant_id, 
            self.schema_id, 
            pformat(doc))
        if parent_uuid is None:
            parent_uuid = ROOT_DOCUMENT_UUID
        local_acl = self.ensureBaseAcl(local_acl)
        key = self.__getPrimaryKey(doc)
        uuid = uuid4().hex
        now = datetime.datetime.utcnow()
        data_doc = {
            "tenant_id": self.tenant_id,
            "schema_id": self.schema_id,
            "uuid": uuid,
            "document_uuid": uuid,
            "document_version_uuid": uuid,
            "parent_uuid": parent_uuid,
            "local_acl": local_acl,
            "is_acl_inherited": is_acl_inherited,
            "is_version": False,
            "created": now,
            "updated": now,
            "data": json.dumps(doc)
            }

        es_service.save(data_doc)


DocumentService.BASE_ACL = [
    "user:admin:rw",
    "group:admin:rw",
]

