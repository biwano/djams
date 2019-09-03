""" Contains the class managing the documents """
from uuid import uuid4
import datetime
import json
import copy
import logging
from pprint import pformat
from .constants import (
    ACL_BASE,
    TENANT_ID,
    SCHEMA_ID,
    LOCAL_ACL,
    INHERIT_ACL,
    ACL,
    CREATED,
    UPDATED,
    DOCUMENT_UUID,
    SELF_UUID,
    PARENT_UUID,
    PATH,
    PATH_SEGMENT,
    PATH_HASH,
    IS_VERSION,
    VERSION,
    DATA,
    ROOT_SCHEMA_ID)
from .esService import EsService
from .schemaService import SchemaService
from .documentHelpers import ensure_aces, as_term_filter


class DocumentService(object):
    """ Class managing documents """
    def __init__(self, tenant_id, context, refresh=False):
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
            acl_filter.append({"prefix": {ACL: ace}})

        query = {"bool": {"must": query,
                          "should": acl_filter}
                 }
        return query

    def get_one(self, query, with_context=True):
        if with_context:
            query = self.contextualize_query(query)
        hit = self.es_service.get_one(self.tenant_id, query=query)
        return hit

    def get_root(self, with_context=True):
        return self.get_by_path("/", with_context=with_context)

    def get_root_uuid(self, with_context=True):
        return self._get_root(with_context=with_context)[DOCUMENT_UUID]

    def get_child_by_path_segment(self, doc, path_segment, with_context=True):
        """ Checks if a key exists without authorization check"""
        doc = self.doc_from_any(doc, with_context)
        query = as_term_filter({
            PARENT_UUID: doc[DOCUMENT_UUID],
            PATH_SEGMENT: path_segment,
            IS_VERSION: False})
        return self.get_one(query, with_context=with_context)

    def delete_child_by_path_segment(self, doc, path_segment, with_context=True):
        doc = self.get_child_by_path_segment(doc, path_segment)
        return self.es_service.delete(doc)

    def contextify(self, doc):
        if doc:
            for doc_ace in doc[ACL]:
                for context_ace in self.context.acl:
                    if doc_ace.startswith(context_ace):
                        return doc
        return None

    def get_by_path(self, path, with_context=True):
        doc = self.es_service.get_by_path_and_version(self.tenant_id, path)
        doc = self.contextify(doc)

        return doc

    def get_by_uuid(self, uuid, with_context=True):
        query = as_term_filter({DOCUMENT_UUID: uuid, IS_VERSION: False})
        return self.get_one(query, with_context=with_context)

    def doc_from_any(self, thing, with_context=True):
        if type(thing) == dict:
            return thing
        elif thing.startswith("/"):
            return self.get_by_path(thing, with_context=with_context)
        else:
            return self.get_by_uuid(thing, with_context=with_context)

    def create_root(self):
        return self.create(ROOT_SCHEMA_ID, parent=None, path_segment=None)

    def set_aliases_be(self, tenant_id, schema_id, source, destination):
        schemaService = SchemaService(tenant_id, schema_id, self.context, self.refresh)
        aliases = schemaService.get_aliases()
        for alias in aliases:
            if aliases[alias] in source:
                destination[alias] = source[aliases[alias]]

    def set_aliases(self, tenant_id, schema_id, source, destination):
        self.set_aliases_be(tenant_id, schema_id, source, destination)
        self.set_aliases_be(tenant_id, schema_id, destination, destination)

    def create(self, schema_id, parent, path_segment, data={}, is_acl_inherited=True, local_acl=None):
        """ Creates a document """
        self.logger.info("Creating document %s.%s: %s",
                         self.tenant_id,
                         schema_id,
                         path_segment)
        self.logger.debug(" => data: %s", pformat(data))

        uuid = uuid4().hex

        # Compute Parent
        if parent is None:
            if self.context.is_tenant_admin():
                parent_uuid = None
            else:
                raise Exception("Only tenant admins can create root documents")
        else:
            parent = self.doc_from_any(parent)
            parent_uuid = parent[SELF_UUID]
        # TODO: Check write access on parent

        # Ensure local acl
        local_acl = self.ensure_base_aces(local_acl)

        # SEtting metadata
        now = datetime.datetime.utcnow()
        metadata = {
            TENANT_ID: self.tenant_id,
            SCHEMA_ID: schema_id,
            LOCAL_ACL: local_acl,
            INHERIT_ACL: is_acl_inherited,
            CREATED: now,
            UPDATED: now,
            DOCUMENT_UUID: uuid,
            SELF_UUID: uuid,
            PARENT_UUID: parent_uuid,
            PATH_SEGMENT: path_segment,
            IS_VERSION: False,
            VERSION: None
        }
        # Setting aliases
        self.set_aliases(self.tenant_id, schema_id, metadata, data)
        # Computing doc
        data_doc = metadata
        data_doc[DATA] = json.dumps(data)

        return self.es_service.create(data_doc, parent)

    def fdms_search(self, schema_id=None, query=None):
        docs = self.es_service.search(self.tenant_id, schema_id, query)
        return docs

    def search(self, schema_id=None, query=None, with_context=True):
        if with_context:
            query = self.contextualize_query(query)
        return self.fdms_search(schema_id, query)
