""" Contains the class that manages schemas """
import logging
import json
import copy
from pprint import pformat
from .constants import (
    SEARCH_MAPPING_BASE,
    SCHEMA_SCHEMA_DEFINITION_DOCUMENT,
    ROOT_SCHEMA_DEFINITION_DOCUMENT,
    FOLDER_SCHEMA_DEFINITION_DOCUMENT,
    FDMS_MAPPING_KEYS,
    SCHEMA_SCHEMA_ID,
    ROOT_SCHEMA_ID,
    FOLDER_SCHEMA_ID,
    SCHEMAS_PATH)
from .esService import EsService
from .cacheService import get_cache
from .documentHelpers import path


class SchemaService(object):
    """  Class managing schemas """
    def __init__(self, tenant_id, schema_id, context, refresh=False):
        self.tenant_id = tenant_id
        self.schema_id = schema_id
        self.es_service = EsService(refresh)
        self.schema_es_index = self.es_service.get_search_index_name(self.tenant_id, SCHEMA_SCHEMA_ID)
        self.es_index = self.es_service.get_search_index_name(self.tenant_id, self.schema_id)
        self.logger = logging.getLogger(type(self).__name__)
        self.context = context
        self.refresh = refresh


    def __get_document(self):
        """ Returns the document containg the schema """
        def __get_document_no_cache():

            from .documentService import DocumentService
            schema = None

            def debug_schema(schema, source):
                if schema:
                    self.logger.debug("schema from %s %s/%s",
                                      source,
                                      self.tenant_id,
                                      self.schema_id)
                return schema

            def get_from_static_definition(schema, schema_id, schema_definition):
                if self.schema_id == schema_id and schema is None:
                    schema = schema_definition
                return debug_schema(schema, "static definition")


            schema = DocumentService(self.tenant_id, self.context).get_by_path(path(SCHEMAS_PATH, self.schema_id))
            if debug_schema(schema, "database"):
                schema["properties"] = json.loads(schema["properties"])
                return schema

            schema = get_from_static_definition(schema, SCHEMA_SCHEMA_ID, SCHEMA_SCHEMA_DEFINITION_DOCUMENT)
            if schema:
                return schema
            schema = get_from_static_definition(schema, ROOT_SCHEMA_ID, ROOT_SCHEMA_DEFINITION_DOCUMENT)
            if schema:
                return schema
            schema = get_from_static_definition(schema, FOLDER_SCHEMA_ID, FOLDER_SCHEMA_DEFINITION_DOCUMENT)
            if schema:
                return schema
            
            raise Exception("Schema not registered yet", self.tenant_id, self.schema_id)

        key = "schema_{}|{}".format(self.tenant_id, self.schema_id)
        document = get_cache().get(key=key,
                                   createfunc=__get_document_no_cache)

        if document == None:
            raise Exception("Cannot find schema definition", key)

        return document

    def get_properties(self):
        """ return the schema properties definition """
        return self.__get_document()["properties"]

    def get_aliases(self):
        """ return the schema properties definition """
        properties = self.get_properties()
        aliases = {}
        for prop in properties:
            if "alias" in properties[prop]:
                aliases[prop] = properties[prop]["alias"]
        return aliases


    def register(self, properties, drop=False, persist=True):
        """ Register a schema """
        from .documentService import DocumentService
        self.logger.info("Registering schema %s/%s",
                         self.tenant_id,
                         self.schema_id)
        self.logger.debug("=> properties: %s", pformat(properties))

        # Create ES index
        mapping_properties = self.__make_es_mapping(properties)
        self.es_service.create_index(self.es_index, mapping_properties, drop)

        # Save the schema document*
        if persist:
            schema_doc = {"properties": json.dumps(properties)}
            document_service = DocumentService(self.tenant_id, self.context, refresh=self.refresh)
            document_service.create(schema_id=SCHEMA_SCHEMA_ID, parent=SCHEMAS_PATH, path_segment=self.schema_id, data=schema_doc)


    def delete(self):
        self.es_service.delete_index(self.es_index)
        get_cache().remove_value(key=self.tenant_id + "|" + self.schema_id)

    @classmethod
    def __make_es_mapping(cls, properties):
        """ Transforms a FDMS mapping into an ES mapping """
        mapping_properties = copy.deepcopy(properties)
        mapping_properties.update(SEARCH_MAPPING_BASE)

        for prop in mapping_properties:
            # Populating aliases
            if "alias" in mapping_properties[prop]:
                alias = mapping_properties[prop]["alias"]
                mapping_properties[prop] = mapping_properties[alias]
            # Removes specific FDMS Keys
            for key in FDMS_MAPPING_KEYS:
                if key in mapping_properties[prop]:
                    del mapping_properties[prop][key]

        return mapping_properties

