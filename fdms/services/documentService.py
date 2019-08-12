""" Contains the class managing the documents """
from uuid import uuid4
import datetime
import json
import logging
from pprint import pformat
from .schemaService import SchemaService
from .constants import ROOT_DOCUMENT_UUID, ACL_BASE
from .esService import EsService


class DocumentService(object):
    """ Class managing documents """
    def __init__(self, tenant_id, context):
        self.tenant_id = tenant_id
        self.logger = logging.getLogger(type(self).__name__)
        self.context = context
        self.es_service = EsService()
        
    def __get_primary_key(self, schema_id, doc):
        """ Returns the primary key of the document """
        schema_service = SchemaService(self.tenant_id, schema_id, self.context)
        primary_key = schema_service.get_primary_key()
        key = {}
        for k in primary_key:
            if k not in doc:
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

    def create(self, schema_id, doc, parent_uuid=None, is_acl_inherited=True, local_acl=None):
        """ Creates a document """
        self.logger.debug("Creating document in schema %s/%s : %s",
                          self.tenant_id,
                          schema_id,
                          pformat(doc))

        if parent_uuid == None:
            if not self.context.is_tenant_admin():
                raise Exception("Not Authorized on root document")
        else:
            #TODO
            pass


        key = self.__get_primary_key(schema_id, doc)
        found_doc = self.es_service.get_by_key(self.tenant_id, schema_id, key)
        if not found_doc:
            if parent_uuid is None:
                parent_uuid = ROOT_DOCUMENT_UUID
            local_acl = self.ensure_base_aces(local_acl)
            uuid = uuid4().hex
            now = datetime.datetime.utcnow()
            data_doc = {
                "tenant_id": self.tenant_id,
                "schema_id": schema_id,
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

            self.es_service.save(data_doc)
        else:
            raise Exception("Document key exists {}/{}/{}".format(self.tenant_id,
                                                                  schema_id,
                                                                  key))

    def search(self, schema_id, query=None):
        docs = self.es_service.search(self.tenant_id, schema_id, query)
        docs = [doc["_source"] for doc in docs]
        return docs