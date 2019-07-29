""" Contains the class that manages schemas """
import logging
import json
from pprint import pformat
from .. import model
from .constants import SEARCH_MAPPING_BASE, SCHEMA_SCHEMA_DEFINITION_DOCUMENT, FDMS_MAPPING_KEYS
from .esService import es_service

class SchemaService(object):
    """  Class managing schemas """
    def __init__(self, tenant_id, schema_id, acls):
        self.tenant_id = tenant_id
        self.schema_id = schema_id
        self.es = model.es
        self.schema_es_index = es_service.get_schema_index_name(self.tenant_id, "schema")
        self.es_index = es_service.get_schema_index_name(self.tenant_id, self.schema_id)
        self.logger = logging.getLogger(type(self).__name__)
        self.acls = acls


    def __cache(self, schema_data):
        """ Puts a schema in cache """
        # expand schema properties before caching
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
        self.logger.info("Registering schema %s/%s with props %s",
                         self.tenant_id,
                         self.schema_id,
                         pformat(properties))

       # Create ES index
        mapping_properties = self.__make_es_mapping(properties)
        es_service.create_index(self.es_index, mapping_properties, drop)

        # Save the schema document
        schema_doc = {"schema_id": self.schema_id, "properties": json.dumps(properties)}
        document_service = DocumentService(self.tenant_id, "schema", self.acls)
        document_service.create(schema_doc)

        # Cache the schema document
        self.__cache(schema_doc)

    @classmethod
    def __make_es_mapping(cls, properties):
        """ Transforms a FDMS mapping into an ES mapping """
        mapping_properties = dict(properties)
        mapping_properties.update(SEARCH_MAPPING_BASE)

        for prop in mapping_properties:
            for key in FDMS_MAPPING_KEYS:
                if key in mapping_properties[prop]:
                    del mapping_properties[prop][key]

        return mapping_properties



SchemaService.cache = {}
