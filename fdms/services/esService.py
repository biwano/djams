""" Contains the class that manages persistence """
import logging
import copy
from pprint import pformat
import json
from elasticsearch import Elasticsearch
from flask import current_app
from .constants import (DATA_MAPPING)
from .documentHelpers import ensure_aces, as_term_filter

#es_service = None


class EsService(object):
    """ Manages persistence """
    def __init__(self, refresh=False):
        self.es = current_app.extensions['elasticsearch']
        self.logger = logging.getLogger(type(self).__name__)
        self.refresh = refresh

    @classmethod
    def get_data_index_name(cls, tenant_id):
        """ Returns the name of a data index """
        return 'tenant.{}.data'.format(tenant_id)

    @classmethod
    def get_search_index_name(cls, tenant_id, schema_id):
        """ Returns the name of a search index """
        return 'tenant.{}.index.{}'.format(tenant_id, schema_id)

    @classmethod
    def get_all_search_index_name(cls, tenant_id):
        """ Returns the name of a search index """
        return 'tenant.{}.index.*'.format(tenant_id)

    @classmethod
    def get_all_tenants_search_index_name(cls):
        """ Returns the name of a search index """
        return 'tenant.*.index.*'

    @classmethod
    def get_search_index_name_auto(cls, tenant_id, schema_id):
        """ Returns the name of a search index """
        if tenant_id:
            if schema_id:
                return cls.get_search_index_name(tenant_id, schema_id)
            else:
                return cls.get_all_search_index_name(tenant_id)
        else:
            return cls.get_all_tenants_search_index_name()

    def get_by_key_filter(self, key):
        filt = []
        for k in key:
            filt.append({"term": {k: key[k]}})
        return filt

    def get_one(self, tenant_id, query):
        index_name = self.get_all_search_index_name(tenant_id)
        result = self.es.search(index=index_name, body={"query": query})
        hits = result["hits"]["hits"]
        self.logger.debug("Get one %s: %s", index_name, pformat(query))
        if len(hits) == 1:
            self.logger.debug("Found: %s", pformat(hits[0]))
            return hits[0]
        if len(hits) > 1:
            raise Exception("Multiple hits for {}/{}".format(index_name, pformat(query)))
        return None
    
    def get_by_uuid(self, tenant_id, uuid):
        # Returns a document by uuid        
        query = as_term_filter({"document_uuid": uuid,
                                "is_version": False})

        return self.get_one(tenant_id, query)
    
    def search(self, tenant_id=None, schema_id=None, query=None):
        """ Returns a document by key """
        index_name = self.get_search_index_name_auto(tenant_id, schema_id)
        if query:
            body = {"query": query}
        else:
            body = None
        self.logger.debug("Search %s: %s", index_name, pformat(body))
        result = self.es.search(index=index_name, body=body)
        hits = result["hits"]["hits"]
        return hits

    def create_index(self, index_name, properties, drop):
        """ Creates an index """
        if drop:
            self.delete_index(index_name)
        self.logger.info("Creating index %s", index_name)
        self.es.indices.create(index=index_name, ignore=400)
        mapping = {"properties": properties}
        self.logger.info("Putting mapping on index %s", index_name)
        self.logger.debug(pformat(mapping))
        self.es.indices.put_mapping(index=index_name, body=mapping)

    def delete_index(self, index_name):
        self.logger.info("Droping index %s", index_name)
        self.es.indices.delete(index_name, ignore=[400, 404])

    def create_data_index(self, tenant_id, drop):
        index_name = self.get_data_index_name(tenant_id)
        self.create_index(index_name, DATA_MAPPING, drop)

    def delete_data_index(self, tenant_id):
        index_name = self.get_data_index_name(tenant_id)
        self.delete_index(index_name)
        
    def delete(self, doc):
        """ deletes a document """
        self.unindex(doc)
        uuid = doc["document_version_uuid"]
        index_name = self.get_data_index_name(doc["tenant_id"])
        self.logger.debug("Deleting document %s/%s refresh = %s", index_name, uuid, self.refresh)
        self.es.delete(index=index_name, id=uuid, refresh=self.refresh)
        
    def save(self, doc, parent=None):
        """ Indexes a document in a data index """
        index_name = self.get_data_index_name(doc["tenant_id"])
        uuid = doc["document_version_uuid"]
        self.logger.debug("Persisting document %s/%s %s refresh = %s", index_name, uuid, pformat(doc), self.refresh)
        self.es.index(index=index_name, id=uuid, body=doc)
        return self.index(doc, parent)

    def index(self, doc, parent=None):
        """ Indexes a document in a search index """
        index_doc = copy.deepcopy(doc)
        index_doc.update(json.loads(doc["data"]))
        uuid = doc["document_version_uuid"]
        # computing acls
        if parent == None:
            if index_doc["is_root"]:
                index_doc["path"] = "/"
                index_doc["acl"] = index_doc["local_acl"]
            else:
                parent = self.get_by_uuid(doc["tenant_id"], doc["parent_uuid"])["_source"]
                if parent["is_root"]:
                    index_doc["path"] = "/" + index_doc["id"]
                else:
                    index_doc["path"] = parent["path"] + "/" + index_doc["id"]
                index_doc["acl"] = ensure_aces(index_doc["local_acl"], parent["acl"])

        del index_doc["data"]
        index_name = self.get_search_index_name(doc["tenant_id"], doc["schema_id"])

        self.logger.debug("Indexing document %s/%s %s refresh = %s", index_name, uuid, pformat(index_doc), self.refresh)
        self.es.index(index=index_name, id=uuid, body=index_doc, refresh=self.refresh)
        return index_doc

    def unindex(self, doc):
        """ de indexes a document"""
        uuid = doc["document_version_uuid"]
        index_name = self.get_search_index_name(doc["tenant_id"], doc["schema_id"])
        self.logger.debug("Unindexing document %s/%s refresh = %s", index_name, uuid, self.refresh)
        self.es.delete(index=index_name, id=uuid, refresh=self.refresh)

class FlaskEs(object):
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(type(self).__name__)
        self.init_app(app)

    def init_app(self, app):
        self.logger.info("Initializing Elasticsearch connection %s", pformat(app.config['ELASTICSEARCH']))
        app.extensions['elasticsearch'] = Elasticsearch(app.config['ELASTICSEARCH'].get("hosts"))

