""" Contains the class managing the documents """
from uuid import uuid4
import datetime
import json
import copy
import logging
import json
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
    PERMISSIONS,
    ALL_PERMISSIONS,
    IS_VERSION,
    VERSION,
    VIEW_CONFIG,
    DATA,
    ROOT_SCHEMA_ID,
    ADMIN_CONTEXT,
    METADATA_FIELDS)
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
        if doc:
            permissions = self.calc_permissions(doc)
            if "r" in permissions:
                return doc
            else:
                self.logger.debug("Permission denied %s context: on %s (%s)",
                                  pformat(doc[ACL]),
                                  pformat(self.context),
                                  permissions)
        return None

    def split_ace(self, ace):
        splited = ace.split(":")
        entity_type = splited[0]
        entity_id = splited[1]
        permission = splited[2] if len(splited) == 3 else None
        return (entity_type, entity_id, permission)

    def calc_permissions(self, doc):
        """ returns the permissions for a given document an the context """
        permissions = ""
        if self.context == ADMIN_CONTEXT:
            permissions = ALL_PERMISSIONS
        else:
            for doc_ace in doc[ACL]:
                (doc_ace_type, doc_ace_id, doc_ace_permission) = self.split_ace(doc_ace)
                for context_ace in self.context.acl:
                    (context_ace_type, context_ace_id, context_ace_permission) = self.split_ace(context_ace)
                    if doc_ace_type == context_ace_type and doc_ace_id == context_ace_id:
                        permissions = permissions + doc_ace_permission
        return permissions

    def add_permissions(self, thing, with_permissions=True):
        """ adds permissions to a document or a list of documents"""
        if with_permissions:
            if type(thing) == list:
                thing = [self.add_permissions(o) for o in thing]
            else:
                if self.context == ADMIN_CONTEXT:
                    permissions = "rw"
                elif thing:
                    thing[PERMISSIONS] = self.calc_permissions(thing)
        return thing

    def search(self, query, schema_id=None):
        query = self.contextualize_query(query)
        self.logger.debug("Searching %s.%s: %s",
                          self.tenant_id,
                          schema_id,
                          pformat(query))
        docs = self.es_service.search(self.tenant_id, schema_id, query)
        docs = [self.decode_data(doc) for doc in docs]
        return docs

    def search_one(self, query):
        query = self.contextualize_query(query)
        hit = self.es_service.search_one(self.tenant_id, query=query)
        hit = self.decode_data(hit)
        return hit

    def get_by_path(self, path, with_permissions=False):
        self.logger.debug("Get by path %s: %s",
                          self.tenant_id,
                          path)
        doc = self.es_service.get_by_path_and_version(self.tenant_id, path)
        doc = self.contextify_doc(doc)
        doc = self.decode_data(doc)
        self.add_permissions(doc, with_permissions)
        return doc

    def search_children(self, doc, filter={}, with_permissions=False):
        parent = self.doc_from_any(doc)
        filter.update({PARENT_UUID: parent[DOCUMENT_UUID], IS_VERSION: False})
        query = as_term_filter(filter)
        children = self.search(query)
        self.add_permissions(children, with_permissions)
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

    def decode_data(self, doc):
        if doc:
            schemaService = SchemaService(doc[TENANT_ID], doc[SCHEMA_ID], self.context, self.refresh)
            properties = schemaService.get_properties()
            for prop in properties:
                definition = properties[prop]
                # Decode json
                if "type" in definition and definition["type"] == "json" and prop in doc:
                    doc[prop] = json.loads(doc[prop])
        return doc

    def encode_data(self, tenant_id, schema_id, data):
        if data:
            schemaService = SchemaService(tenant_id, schema_id, self.context, self.refresh)
            properties = schemaService.get_properties()
            for prop in properties:
                definition = properties[prop]
                # Encode json
                if "type" in definition and definition["type"] == "json" and prop in data:
                    data[prop] = json.dumps(data[prop])
        return data

    def set_aliases_be(self, tenant_id, schema_id, source, destination):
        schemaService = SchemaService(tenant_id, schema_id, self.context, self.refresh)
        aliases = schemaService.get_aliases()
        for alias in aliases:
            if aliases[alias] in source:
                destination[alias] = source[aliases[alias]]

    def set_aliases(self, tenant_id, schema_id, source, destination):
        self.set_aliases_be(tenant_id, schema_id, source, destination)
        self.set_aliases_be(tenant_id, schema_id, destination, destination)

    def get_document_metadata(self, doc):
        metadata = {}
        for field in METADATA_FIELDS:
            metadata[field] = doc[field]
        return metadata


    def create(self, schema_id, parent, path_segment, data={}, is_acl_inherited=True, local_acl=None, view_config=None):
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


        # Ensure local acl
        local_acl = self.ensure_base_aces(local_acl)

        # Setting metadata
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
            VERSION: None,
            VIEW_CONFIG: view_config
        }
        # Setting aliases
        self.set_aliases(self.tenant_id, schema_id, metadata, data)
        self.encode_data(self.tenant_id, schema_id, data)
        # Computing doc
        data_doc = metadata
        data_doc[DATA] = json.dumps(data)

        return self.es_service.create(data_doc, parent)

    def update(self, doc, data={}):
        """ Updates a document """
        self.logger.info("Updating document %s.%s",
                         self.tenant_id
                        )
        self.logger.debug(" => data: %s", pformat(data))
        doc = self.doc_from_any(doc)
        if not doc:
            raise Exception("Document not found")

        # remove non known schema properties from data
        schemaService = SchemaService(doc[TENANT_ID], doc[SCHEMA_ID], self.context, self.refresh)
        properties = schemaService.get_properties()
        for key in list(data):
            if key not in properties or key.startswith("_"):
                del data[key]

        # Setting metadata
        metadata = self.get_document_metadata(doc)
        metadata[UPDATED] = datetime.datetime.utcnow()
        metadata[PATH] = doc[PATH]

        # Setting aliases
        self.set_aliases(self.tenant_id, doc[SCHEMA_ID], metadata, data)
        self.encode_data(self.tenant_id, doc[SCHEMA_ID], data)
        # Computing doc
        data_doc = metadata
        data_doc[DATA] = json.dumps(data)

        print(data_doc)
        return self.es_service.update(data_doc)

    def create_root(self):
        return self.create(ROOT_SCHEMA_ID, parent=None, path_segment="root")


