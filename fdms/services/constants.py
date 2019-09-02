""" Services shared contants """
import json
# The FDMS mapping of the schema document type
SCHEMA_SCHEMA_DEFINITION = {
    "properties": {"type": "text", "index": False},

}
# The FDMS mapping of the user document type
USER_SCHEMA_DEFINITION = {
    "is_tenant_admin": {"type": "boolean"},
}
# The FDMS mapping of the group document type
GROUP_SCHEMA_DEFINITION = {
    "users": {"type": "keyword"},
}
# The FDMS mapping of the group document type
FOLDER_SCHEMA_DEFINITION = {
}
# The FDMS mapping of the group document type
ROOT_SCHEMA_DEFINITION = {
}
# The FDMS mapping of the group document type
TENANT_SCHEMA_DEFINITION = {
}
# The document containing the FDMS mapping of the schema document type
SCHEMA_SCHEMA_DEFINITION_DOCUMENT = {
    "properties": SCHEMA_SCHEMA_DEFINITION
}
# The document containing the FDMS mapping of the folder document type
ROOT_SCHEMA_DEFINITION_DOCUMENT = {
    "properties": ROOT_SCHEMA_DEFINITION
}
# Master tenant (contains metadata about other tenants)
TENANT_MASTER = "fdms"

# Base properties
PROPERTIES_BASE = {
    # tenant_id: tenant id of this entry
    "tenant_id": {"type": "keyword"},
    # schema_id: schema id of this entry
    "schema_id": {"type": "keyword"},
    # local_acl: acl for this enrry
    "local_acl": {"type": "keyword"},
    # inherited acl: true if this entry acl is based on the parent acls
    "inherit_acl": {"type": "boolean"},
    # acls: computed by es using  local_acl and parent_acl if inherit_acl is true
    "acl": {"type": "keyword"},
    # created: date of creation of this entry
    "created": {"type": "date"},
    # updated: date of the last update of this entry
    "updated": {"type": "date"},
    # document_uuid: uuid of the document (equals to self_uuid if this entry is a document)
    "document_uuid": {"type": "keyword"},
    # self_uuid: uuid of this entry
    "self_uuid": {"type": "keyword"},
    # parent_uuid: uuid of the parent document
    "parent_uuid": {"type": "keyword"},
    # path: computed by es using parent path and path_segment
    "path": {"type": "keyword"},
    # path_segment: unique identifier of a document in the brotherhood
    "path_segment": {"type": "keyword"},
    # path_hash: computed by es using path and version, used as the id in elasticsearch for true uniqueness
    "path_hash": {"type": "keyword"},
    # version: version of the entry (is None for documents)
    "version": {"type": "keyword"}
}
# Mapping of the data indexes
DATA_MAPPING = dict(PROPERTIES_BASE)
DATA_MAPPING.update({
    "data" :  {"type" : "text", "index": False}
})
# Base mapping of the search indexes
SEARCH_MAPPING_BASE = dict(PROPERTIES_BASE)
SEARCH_MAPPING_BASE.update({
})
# Root document uuid
ROOT_DOCUMENT = { 
  "document_uuid": "1074e4d0f328444bb8bcf6cd4e13dbbb",
  "acls": [],
  "path": "/",
}

# pure FDMS properties in mappings (must be removed for creating an ES mapping)
FDMS_MAPPING_KEYS = ["key"]

# acl provided by the tenant service
TENANT_ACES = ["group:admin"]


# base acl on all documents to enable all operations for the tenant and the administrators
ACL_BASE = [
    "group:admin:rw",
]
