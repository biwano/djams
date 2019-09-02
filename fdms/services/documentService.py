""" Contains the class managing the documents """
from uuid import uuid4
import datetime
import json
import logging
from pprint import pformat
from .schemaService import SchemaService
from .constants import ROOT_DOCUMENT, ACL_BASE
from .esService import EsService
from .documentHelpers import ensure_aces, as_term_filter


class DocumentService(object):
    """ Class managing documents """
    def __init__(self, tenant_id, context, refresh = False):
        self.tenant_id = tenant_id
        self.logger = logging.getLogger(type(self).__name__)
        self.context = context
        self.refresh = refresh
        self.es_service = EsService(refresh)
        
    @classmethod
    def ensure_base_aces(cls, local_acl):
        """ Ensures that base aces are in the local_acl """
        return ensure_aces(local_acl, ACL_BASE)

    def contextualize_query(self, query):
        acl_filter = []
        for ace in self.context.acl:
            acl_filter.append({"prefix" : {"acl" : ace}})

        query = {"bool":{"must" : query,
                         "should": acl_filter}
                }
        return query

    def get_one(self, query, with_context=True):
        if with_context:
            query = self.contextualize_query(query)
        hit = self.es_service.get_one(self.tenant_id, query=query)
        return hit

#    def get_root(self, with_context=True):
#        query = as_term_filter({"is_root": True, "schema_id": "root", "id": "root", "is_version": False})
#        return self.get_one(query, with_context=with_context)

#    def get_root_uuid(self):
#        return self._get_root()["document_uuid"]

    def get_child_by_id(self, doc, child_id, with_context=True):
        """ Checks if a key exists without authorization check"""
        doc = self.doc_from_any(doc, with_context)
        query = as_term_filter({
            "parent_uuid": doc["document_uuid"],
            "id": child_id,
            "is_version": False})
        return self.get_one(query, with_context=with_context)

    def delete_child_by_id(self, doc, child_id, with_context=True):
        doc = self.get_child_by_id(doc, child_id)
        return self.es_service.delete(doc)

    def get_by_path(self, path, with_context=True):
        query = as_term_filter({"path": path, "is_version": False})
        return self.get_one(query, with_context=with_context)

    def get_by_uuid(self, uuid, with_context=True):
        query = as_term_filter({"document_uuid": uuid, "is_version": False})
        return self.get_one(query, with_context=with_context)

    def doc_from_any(self, thing, with_context=True):
        if type(thing) == dict:
            return thing
        elif thing.startswith("/"):
            return self.get_by_path(thing, with_context=with_context)
        else:
            return self.get_by_uuid(thing, with_context=with_context)

    def create_root(self):
        return self.create("root", parent=None, path_segment=None)

    def create(self, schema_id, parent, path_segment, data={}, is_acl_inherited=True, local_acl=None):
        """ Creates a document """
        self.logger.debug("Creating document in schema %s/%s : %s",
                          self.tenant_id,
                          schema_id,
                          pformat(data))

        uuid = uuid4().hex

        # Compute Parent
        if parent==None:
            if self.context.is_tenant_admin():
                parent_uuid = None
            else:
                raise Exception("Only tenant admins can create root documents")
        else:
            parent = self.doc_from_any(parent)
            parent_uuid = parent["self_uuid"]
        # TODO: Check write access on parent

        # Compute acl
        local_acl = self.ensure_base_aces(local_acl)

        now = datetime.datetime.utcnow()
        data_doc = {
            "tenant_id": self.tenant_id,
            "schema_id": schema_id,
            "path_segment": path_segment,
            "self_uuid": uuid,
            "document_uuid": uuid,
            "parent_uuid": parent_uuid,
            "local_acl": local_acl,
            "is_acl_inherited": is_acl_inherited,
            "is_version": False,
            "version": None,
            "created": now,
            "updated": now,
            "data": json.dumps(data)
            }

        return self.es_service.create(data_doc, parent)

    def fdms_search(self, schema_id=None, query=None):
        docs = self.es_service.search(self.tenant_id, schema_id, query)
        return docs

    def search(self, schema_id=None, query=None, with_context=True):
        if with_context:
            query = self.contextualize_query(query)
        return self.fdms_search(schema_id, query)
