import logging
from pprint import pformat
import json
from fdms import model

class EsService():
    def __init__(self):
        self.es = model.es
        self.logger = logging.getLogger(type(self).__name__)

    def getDataIndexName(self, tenant_id):
        return '{}.data'.format(tenant_id)

    def getSchemaIndexName(self, tenant_id, schema_id):
        return '{}.index.{}'.format(tenant_id, schema_id)

    def createIndex(self, index_name, properties, drop):
        if drop:
            self.logger.info("Droping index %s", index_name)
            self.es.indices.delete(index_name, ignore=[400, 404])
        self.logger.info("Creating index %s", index_name)
        self.es.indices.create(index=index_name, ignore=400)
        mapping = {"properties": properties}
        self.logger.info("Putting mapping on index %s : %s", index_name, pformat(mapping))
        self.es.indices.put_mapping(index=index_name, body=mapping)

    def save(self, doc):
        index_name = self.getDataIndexName(doc["tenant_id"])
        id = doc["uuid"]
        self.logger.debug("Persisting document %s/%s %s", index_name, id, pformat(doc))
        self.es.index(index=index_name, id=id, body=doc)
        self.index(doc)

    def index(self, doc):
        index_doc = dict(doc)
        index_doc.update(json.loads(doc["data"]))
        id = doc["uuid"]
        del index_doc["data"]
        index_name = self.getSchemaIndexName(doc["tenant_id"], doc["schema_id"])
        self.logger.debug("Indexing document %s/%s %s", index_name, id, pformat(index_doc))
        self.es.index(index=index_name, id=id, body=index_doc)



es_service = EsService()