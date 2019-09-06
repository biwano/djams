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
    ROOT_SCHEMA_ID,
    ADMIN_CONTEXT)
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
        """ Transforms a query so it returns only visible documents given the context """
        if self.context == ADMIN_CONTEXT:
            return query
        acl_filter = []
        for ace in self.context.acl:
            acl_filter.append({"prefix": {ACL: ace}})

        query = {"bool": {"must": query,
                          "should": acl_filter}
                 }
        return query

    def contextify_doc(self, doc):
        """ Returns None if the context does not give visibility to the document """
        if self.context == ADMIN_CONTEXT:
            return doc
        if doc:
            for doc_ace in doc[ACL]:
                for context_ace in self.context.acl:
                    if doc_ace.startswith(context_ace):
                        return doc
        return None

    def search(self, query, schema_id=None):
        query = self.contextualize_query(query)
        self.logger.debug("Searching %s.%s: %s",
                          self.tenant_id,
                          schema_id,
                          pformat(query))
        docs = self.es_service.search(self.tenant_id, schema_id, query)
        return docs

    def search_one(self, query):
        query = self.contextualize_query(query)
        hit = self.es_service.search_one(self.tenant_id, query=query)
        return hit

    def get_by_path(self, path):
        self.logger.debug("Get by path %s: %s",
                          self.tenant_id,
                          path)
        doc = self.es_service.get_by_path_and_version(self.tenant_id, path)
        doc = self.contextify_doc(doc)
        return doc

    def search_children(self, doc, filter={}):
        parent = self.doc_from_any(doc)
        filter.update({PARENT_UUID: parent[DOCUMENT_UUID], IS_VERSION: False})
        query = as_term_filter(filter)
        children = self.search(query)
        return children

    def get_root(self):
        return self.get_by_path("/")

    def get_root_uuid(self):
        return self.get_root()[DOCUMENT_UUID]

    def search_by_uuid(self, uuid):
        if len(uuid) != 32:
            raise Exception("Malformed UUID")
        query = as_term_filter({DOCUMENT_UUID: uuid, IS_VERSION: False})
        return self.search_one(query)

    def doc_from_any(self, thing):
        """ Returns a contextualized version of doc wether doc is an uuid, a path or a document"""
        if type(thing) == dict:
            return self.contextify_doc(thing)
        elif thing.startswith("/"):
            return self.get_by_path(thing)
        else:
            return self.search_by_uuid(thing)

    def delete(self, doc):
        doc = self.doc_from_any(doc)
        return self.es_service.delete(doc)

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

        if "|" in path_segment or "/" in path_segment:
            raise Exception("Invalid path segment")

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

    def create_root(self):
        return self.create(ROOT_SCHEMA_ID, parent=None, path_segment="root")


