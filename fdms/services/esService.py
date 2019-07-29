""" Contains the class that manages persistence """
import logging
from pprint import pformat
import json
from fdms import model

class EsService(object):
    """ Manages persistence """
    def __init__(self):
        self.es = model.es
        self.logger = logging.getLogger(type(self).__name__)

    @classmethod
    def get_data_index_name(cls, tenant_id):
        """ Returns the name of a data index """
        return '{}.data'.format(tenant_id)

    @classmethod
    def get_schema_index_name(cls, tenant_id, schema_id):
        """ Returns the name of a search index """
        return '{}.index.{}'.format(tenant_id, schema_id)

    def create_index(self, index_name, properties, drop):
        """ Creates an index """
        if drop:
            self.logger.info("Droping index %s", index_name)
            self.es.indices.delete(index_name, ignore=[400, 404])
        self.logger.info("Creating index %s", index_name)
        self.es.indices.create(index=index_name, ignore=400)
        mapping = {"properties": properties}
        self.logger.info("Putting mapping on index %s : %s", index_name, pformat(mapping))
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
        index_doc = dict(doc)
        index_doc.update(json.loads(doc["data"]))
        uuid = doc["uuid"]
        del index_doc["data"]
        index_name = self.get_schema_index_name(doc["tenant_id"], doc["schema_id"])
        self.logger.debug("Indexing document %s/%s %s", index_name, uuid, pformat(index_doc))
        self.es.index(index=index_name, id=uuid, body=index_doc)

es_service = EsService()
