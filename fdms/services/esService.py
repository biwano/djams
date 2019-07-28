from .. import model
import logging

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
        self.logger.info("Putting mapping on index %s : %s", index_name, mapping)
        self.es.indices.put_mapping(index=index_name, body=mapping)

    def save(self, doc):
        index_name = self.getDataIndexName(doc["tenant_id"])
        self.es.index(index=index_name, id=doc["uuid"], body=doc)
        self.index(doc)

    def index(self, doc):
        index_doc = dict(doc)
        index_doc.update(doc["data"])
        del index_doc["data"]
        index_name = self.getSchemaIndexName(doc["tenant_id"], doc["schema_id"])
        self.es.index(index=index_name, id=doc["uuid"], body=doc)



es_service = EsService()