""" Contains the class that manages schemas """
import logging
import json
import copy
from pprint import pformat
from .constants import SEARCH_MAPPING_BASE, SCHEMA_SCHEMA_DEFINITION_DOCUMENT, FDMS_MAPPING_KEYS
from .esService import EsService

class SchemaService(object):
    """  Class managing schemas """
    def __init__(self, tenant_id, schema_id, context):
        self.tenant_id = tenant_id
        self.schema_id = schema_id
        self.es_service = EsService()
        self.schema_es_index = self.es_service.get_search_index_name(self.tenant_id, "schema")
        self.es_index = self.es_service.get_search_index_name(self.tenant_id, self.schema_id)
        self.logger = logging.getLogger(type(self).__name__)
        self.context = context


    def __cache(self, schema_data):
        """ Puts a schema in cache """
        # expand schema properties before caching
        self.logger.debug("Caching schema %s/%s: %s",
                          self.tenant_id,
                          self.schema_id,
                          pformat(schema_data))
        schema_data["properties"] = json.loads(schema_data["properties"])
        SchemaService.cache[self.es_index] = schema_data


    def __get_document(self):
        """ Returns the document containg the schema """
        # get from cache
        schema = SchemaService.cache.get(self.es_index)
        # get from index
        # TODO

        # get from constants if it is the schema schema (because it may not be indexed yet)
        if self.schema_id == "schema" and schema is None:
            schema = SCHEMA_SCHEMA_DEFINITION_DOCUMENT
        return schema

    def get_properties(self):
        """ return the schema properties definition """
        return self.__get_document()["properties"]

    def get_primary_key(self):
        """ return the primary key of the schema """
        properties = self.get_properties()
        primary_key = []
        for prop in properties:
            if properties[prop].get("key") != None:
                primary_key.append(prop)
        if not primary_key:
            primary_key = ["document_version_uuid"]
        return primary_key
    

    def register(self, properties, drop=False):
        """ Register a schema """
        from .documentService import DocumentService
        self.logger.info("Registering schema %s/%s",
                         self.tenant_id,
                         self.schema_id)
        self.logger.debug(pformat(properties))

       # Create ES index
        mapping_properties = self.__make_es_mapping(properties)
        self.es_service.create_index(self.es_index, mapping_properties, drop)

        # Save the schema document
        schema_doc = {"id": self.schema_id, "properties": json.dumps(properties)}
        document_service = DocumentService(self.tenant_id, self.context)
        document_service.create("schema", schema_doc)

        # Cache the schema document
        self.__cache(schema_doc)

    @classmethod
    def __make_es_mapping(cls, properties):
        """ Transforms a FDMS mapping into an ES mapping """
        mapping_properties = copy.deepcopy(properties)
        mapping_properties.update(SEARCH_MAPPING_BASE)

        for prop in mapping_properties:
            for key in FDMS_MAPPING_KEYS:
                if key in mapping_properties[prop]:
                    del mapping_properties[prop][key]

        return mapping_properties



SchemaService.cache = {}
