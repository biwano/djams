""" Contains the class that manages schemas """
import logging
import json
import copy
from pprint import pformat
from .constants import (
    SEARCH_MAPPING_BASE,
    FDMS_MAPPING_KEYS,
    SCHEMA_SCHEMA_ID,
    SCHEMAS_PATH)
from .esService import EsService
from .cacheService import get_cache
from .documentHelpers import path
from .schemaHelpers import get_schema


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
        return get_schema(self.tenant_id, self.schema_id, self.context)

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


    def register(self, document, drop=False, persist=True):
        """ Register a schema """
        from .documentService import DocumentService
        self.logger.info("Registering schema %s/%s",
                         self.tenant_id,
                         self.schema_id)
        self.logger.debug("=> document: %s", pformat(document))
        properties = document["properties"]
        facets = document["facets"]

        # Create ES index
        mapping_properties = self.__make_es_mapping(properties)
        self.es_service.create_index(self.es_index, mapping_properties, drop)

        # Save the schema document*
        if persist:
            schema_doc = {"properties": properties, "facets": facets}
            document_service = DocumentService(self.tenant_id, self.context, refresh=self.refresh)
            document_service.create(schema_id=SCHEMA_SCHEMA_ID, parent=SCHEMAS_PATH, path_segment=self.schema_id, data=schema_doc)


    def delete(self):
        self.es_service.delete_index(self.es_index)
        key = "schema_{}|{}".format(self.tenant_id, self.schema_id)
        get_cache().remove_value(key=key)

    @classmethod
    def __make_es_mapping(cls, properties):
        """ Transforms a FDMS mapping into an ES mapping """
        mapping_properties = copy.deepcopy(properties)
        mapping_properties.update(SEARCH_MAPPING_BASE)

        for prop in mapping_properties:
            definition = mapping_properties[prop]
            # Populating aliases
            if "alias" in definition:
                alias = mapping_properties[prop]["alias"]
                mapping_properties[prop] = mapping_properties[alias]

            # Computing special types
            if "type" in definition and definition["type"] == "json":
                definition["type"] = "text"
                definition["index"] = False

            # Removes specific FDMS Keys
            for key in FDMS_MAPPING_KEYS:
                if key in definition:
                    del definition[key]

        return mapping_properties

