""" Contains the class managing the documents """
from uuid import uuid4
import datetime
import json
import logging
from pprint import pformat
from .schemaService import SchemaService
from .constants import ROOT_DOCUMENT_UUID, ACL_BASE
from .esService import es_service


class DocumentService(object):
    """ Class managing documents """
    def __init__(self, tenant_id, schema_id, acls):
        self.tenant_id = tenant_id
        self.schema_id = schema_id
        self.schema_service = SchemaService(tenant_id, schema_id, acls)
        self.schema = self.schema_service.get_properties()
        self.logger = logging.getLogger(type(self).__name__)
        self.acls = acls

    def __get_primary_key(self, doc):
        """ Returns the primary key of the document """
        primary_key = self.schema_service.get_primary_key()
        key = {}
        for k in primary_key:
            if not k in doc:
                raise Exception("Invalid document key {}/{}/{} expected {}".format(self.tenant_id,
                                                                                   self.schema_id,
                                                                                   pformat(doc),
                                                                                   pformat(primary_key)))
            key[k] = doc[k]
        return key

    @classmethod
    def ensure_base_aces(cls, local_acl):
        """ Ensures that base aces are in the local_acl """
        if local_acl is None:
            local_acl = []
        for ace in ACL_BASE:
            if ace not in local_acl:
                local_acl.append(ace)
        return local_acl

    def create(self, doc, parent_uuid=None, is_acl_inherited=True, local_acl=None):
        """ Creates a document """
        self.logger.debug("Creating document in schema %s/%s : %s",
                          self.tenant_id,
                          self.schema_id,
                          pformat(doc))
        key = self.__get_primary_key(doc)
        found_doc = es_service.find_by_key(self.tenant_id, self.schema_id, key)
        if not found_doc:
            if parent_uuid is None:
                parent_uuid = ROOT_DOCUMENT_UUID
            local_acl = self.ensure_base_aces(local_acl)
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
        else:
            raise Exception("Document key exists {}/{}/{}".format(self.tenant_id,
                                                                  self.schema_id,
                                                                  key))
