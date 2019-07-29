""" Contains the class that manages schemas """
import logging
import json
from pprint import pformat
from .. import model
from .constants import SEARCH_MAPPING_BASE, SCHEMA_SCHEMA_DEFINITION_DOCUMENT, FDMS_MAPPING_KEYS
from .esService import es_service

class SchemaService():
    def __init__(self, tenant_id, schema_id):
        self.tenant_id = tenant_id
        self.es = model.es
        self.schema_index = self.getSchemaIndexName("schema")
        self.schema_id = schema_id
        self.logger = logging.getLogger(type(self).__name__)

    def getSchemaIndexName(self, schema_id):
        return '{}.index.{}'.format(self.tenant_id, schema_id)

    def getIndexName(self):
        return self.getSchemaIndexName(self.schema_id)

    def __cache(self, schema_data):
        index_name = self.getIndexName()
        schema_data["properties"] = json.loads(schema_data["properties"])
        SchemaService.cache[index_name] = schema_data


    def __getDocument(self):
        index_name = self.getIndexName()
        schema = SchemaService.cache.get(index_name)
        if self.schema_id == "schema" and schema is None:
            schema = SCHEMA_SCHEMA_DEFINITION_DOCUMENT
        return schema

    def getProperties(self):
        return self.__getDocument()["properties"]

    def getPrimaryKey(self):
        properties = self.getProperties()
        primary_key = []
        for prop in properties:
            if properties[prop].get("key") != None:
                primary_key.append(prop)
        if not primary_key: 
            primary_key = ["document_version_uuid"] 
        return primary_key

    def register(self, properties, drop = False):
        from .documentService import DocumentService
        self.logger.info("Registering schema %s/%s with props %s", 
            self.tenant_id, 
            self.schema_id, 
            pformat(properties))
       
        mapping_properties = self.makeEsMapping(properties)
        index_name = self.getIndexName()
        es_service.createIndex(index_name, mapping_properties, drop)
        
        schema_doc = {"schema_id": self.schema_id, "properties": json.dumps(properties)}
        document_service = DocumentService(self.tenant_id, "schema")
        document_service.create(schema_doc)

        self.__cache(schema_doc)

    def makeEsMapping(self, properties):
        mapping_properties = dict(properties)
        mapping_properties.update(SEARCH_MAPPING_BASE)

        for prop in mapping_properties:
            for key in FDMS_MAPPING_KEYS:
                if key in mapping_properties[prop]:
                    del mapping_properties[prop][key]

        return mapping_properties



SchemaService.cache = {}
    
