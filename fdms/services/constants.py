""" Services shared contants """
import json
# The FDMS mapping of the schema document type
SCHEMA_SCHEMA_DEFINITION = {
    "id": {"type": "keyword", "key": True},
    "properties": {"type": "text", "index": False},
}
# The document containng the FDMS mapping of the schema document type
SCHEMA_SCHEMA_DEFINITION_DOCUMENT = {
    "id": "schema",
    "properties" : SCHEMA_SCHEMA_DEFINITION,
}
# The FDMS mapping of the user document type
USER_SCHEMA_DEFINITION = {
    "id": {"type": "keyword", "key": True},
    "is_tenant_admin": {"type": "boolean"},
}
# The FDMS mapping of the group document type
GROUP_SCHEMA_DEFINITION = {
    "id": {"type": "keyword", "key": True},
    "users": {"type": "keyword"},
}
# The FDMS mapping of the group document type
TENANT_SCHEMA_DEFINITION = {
    "id": {"type": "keyword", "key": True},
}
# Master tenant (contains metadata about other tenants)
TENANT_MASTER = "fdms"

# Base properties
PROPERTIES_BASE = {
    "schema_id": {"type": "keyword"},
    "tenant_id": {"type": "keyword"},
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

# acl provided by the tenant service
TENANT_ACES = ["group:admin"]


# base acl on all documents to enable all operations for the tenant and the administrators
ACL_BASE = [
    "group:admin:rw",
]
