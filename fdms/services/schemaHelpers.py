""" Helper functions for documents """
import logging
import json
from .constants import (
    SCHEMA_SCHEMA_DOCUMENT,
    ROOT_SCHEMA_DOCUMENT,
    FOLDER_SCHEMA_DOCUMENT,
    SCHEMA_SCHEMA_ID,
    ROOT_SCHEMA_ID,
    FOLDER_SCHEMA_ID,
    SCHEMAS_PATH)
from .cacheService import get_cache
from .documentHelpers import path


def get_schema(tenant_id, schema_id, context):
    logger = logging.getLogger("SchemaService")
    """ Ensures that base aces are in the local_acl """
    def __get_document_no_cache():

        from .documentService import DocumentService
        schema = None

        def debug_schema(schema, source):
            if schema:
                logger.debug("schema from %s %s/%s",
                             source,
                             tenant_id,
                             schema_id)
            return schema

        def get_from_static_definition(schema, static_schema_id, schema_definition):
            if schema_id == static_schema_id and schema is None:
                schema = schema_definition
            return debug_schema(schema, "static definition")


        schema = get_from_static_definition(schema, SCHEMA_SCHEMA_ID, SCHEMA_SCHEMA_DOCUMENT)
        if schema:
            return schema

        schema = DocumentService(tenant_id, context).get_by_path(path(SCHEMAS_PATH, schema_id))
        if debug_schema(schema, "database"):
            #schema["properties"] = json.loads(schema["properties"])
            return schema

        schema = get_from_static_definition(schema, ROOT_SCHEMA_ID, ROOT_SCHEMA_DOCUMENT)
        if schema:
            return schema
        schema = get_from_static_definition(schema, FOLDER_SCHEMA_ID, FOLDER_SCHEMA_DOCUMENT)
        if schema:
            return schema

        raise Exception("Schema not registered yet", tenant_id, schema_id)

    key = "schema_{}|{}".format(tenant_id, schema_id)
    document = get_cache().get(key=key,
                               createfunc=__get_document_no_cache)

    if document == None:
        raise Exception("Cannot find schema definition", key)

    return document
