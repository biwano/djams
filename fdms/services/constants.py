SCHEMA_SCHEMA_DEFINITION = {
    "id": {"type": "keyword", "key": True},
    "properties": {"type": "object"},
}
SCHEMA_SCHEMA_DEFINITION_DOCUMENT = {
    "id": "schema",
    "properties" : SCHEMA_SCHEMA_DEFINITION
}
PROPERTIES_BASE = {
    "local_acls": {"type": "keyword"},
    "inherit_acls": {"type": "boolean"},
    "created": {"type": "date"},
    "updated": {"type": "date"},
    "document_uuid": {"type": "keyword"},
    "document_version_uuid": {"type": "keyword"},
    "parent_uuid": {"type": "keyword"},
    "data" :  {"type" : "object"}
}
DATA_MAPPING = dict(PROPERTIES_BASE)
DATA_MAPPING.update({
    "data" :  {"type" : "object"}
})
SEARCH_MAPPING_BASE = dict(PROPERTIES_BASE)
SEARCH_MAPPING_BASE.update({
    "acls": {"type": "keyword"}
})

ROOT_DOCUMENT_UUID="1074e4d0f328444bb8bcf6cd4e13dbbb"

FDMS_MAPPING_KEYS = ["key"]