""" Services shared contants """
import json

# The FDMS mapping of the schema document type
SCHEMA_SCHEMA_DEFINITION = {
    "schema_id": {"type": "keyword", "key": True},
    "properties": {"type": "text", "index": False},
    "key" : {"type" : "keyword"}
}
# The document containng the FDMS mapping of the schema document type
SCHEMA_SCHEMA_DEFINITION_DOCUMENT = {
    "schema_id": "schema",
    "properties" : SCHEMA_SCHEMA_DEFINITION
}
# Base properties
PROPERTIES_BASE = {
    "local_acls": {"type": "keyword"},
    "inherit_acls": {"type": "boolean"},
    "created": {"type": "date"},
    "updated": {"type": "date"},
    "document_uuid": {"type": "keyword"},
    "document_version_uuid": {"type": "keyword"},
    "parent_uuid": {"type": "keyword"},
}
# Mapping of the data indexes
DATA_MAPPING = dict(PROPERTIES_BASE)
DATA_MAPPING.update({
    "data" :  {"type" : "text", "index": False}
})
# Base mapping of the search indexes
SEARCH_MAPPING_BASE = dict(PROPERTIES_BASE)
SEARCH_MAPPING_BASE.update({
    "acls": {"type": "keyword"}
})
# Root document uuid
ROOT_DOCUMENT_UUID="1074e4d0f328444bb8bcf6cd4e13dbbb"

# pure FDMS properties in mappings (must be removed for creating an ES mapping)
FDMS_MAPPING_KEYS = ["key"]