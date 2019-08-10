""" Contains the class that manages persistence """
import logging
import copy
from pprint import pformat
import json
from elasticsearch import Elasticsearch
from flask import current_app

es_service = None


class EsService(object):
    """ Manages persistence """
    def __init__(self):
        self.es = current_app.extensions['elasticsearch']
        self.logger = logging.getLogger(type(self).__name__)

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


    def get_by_key(self, tenant_id, schema_id, key):
        """ Returns a document by key """
        index_name = self.get_search_index_name(tenant_id, schema_id)
        filt = []
        for k in key:
            filt.append({"term": {k: key[k]}})
        body = {"query": {"bool": {"filter": filt}}}
        self.logger.debug("Find by key %s: %s", index_name, pformat(body))
        result = self.es.search(index=index_name, body=body, size=1)
        hits = result["hits"]["hits"]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            raise Exception("Multiple keys for {}/{}/{}".format(tenant_id, schema_id, pformat(key)))
        return None

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
            self.logger.info("Droping index %s", index_name)
            self.es.indices.delete(index_name, ignore=[400, 404])
        self.logger.info("Creating index %s", index_name)
        self.es.indices.create(index=index_name, ignore=400)
        mapping = {"properties": properties}
        self.logger.info("Putting mapping on index %s", index_name)
        self.logger.debug(pformat(mapping))
        self.es.indices.put_mapping(index=index_name, body=mapping)

    def save(self, doc):
        """ Indexes a document in a data index """
        index_name = self.get_data_index_name(doc["tenant_id"])
        uuid = doc["uuid"]
        self.logger.debug("Persisting document %s/%s %s", index_name, uuid, pformat(doc))
        self.es.index(index=index_name, id=uuid, body=doc)
        self.index(doc)

    def index(self, doc):
        """ Indexes a document in a search index """
        index_doc = copy.deepcopy(doc)
        index_doc.update(json.loads(doc["data"]))
        uuid = doc["uuid"]
        del index_doc["data"]
        index_name = self.get_search_index_name(doc["tenant_id"], doc["schema_id"])
        self.logger.debug("Indexing document %s/%s %s", index_name, uuid, pformat(index_doc))
        self.es.index(index=index_name, id=uuid, body=index_doc)

class FlaskEs(object):
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(type(self).__name__)
        self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('ELASTICSEARCH', {})
        self.logger.info("Initializing Elasticsearch connection %s", pformat(app.config['ELASTICSEARCH']))
        app.extensions['elasticsearch'] = Elasticsearch(app.config['ELASTICSEARCH'].get("hosts"))

