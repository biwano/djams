""" Services shared contants """

# Built in entries
TENANT_MASTER_ID = "__root"
SCHEMA_SCHEMA_ID = "__schema"
GROUP_SCHEMA_ID = "__group"
USER_SCHEMA_ID = "__user"
FOLDER_SCHEMA_ID = "__folder"
ROOT_SCHEMA_ID = "__root"
TENANT_SCHEMA_ID = "__tenant"
CONFIG_SCHEMA_ID = "__config"
VIEW_CONFIG = "__view_config"
VIEW_DEFAULT = "__default"
VIEW_DOCUMENT = "__document"
VIEW_GROUP_DOCUMENT = "__group"
VIEW_GROUPS_FOLDER = "__groups_list"
VIEW_USER_DOCUMENT = "__user"
VIEW_USERS_FOLDER = "__users_list"
VIEW_CONFIG_DOCUMENT = "__config"
PERMISSIONS = "__permissions"
DOCUMENT_VIEWS_PATH_SEGMENT = "document_views"

META_PATH_SEGMENT = "meta"
USERS_PATH_SEGMENT = "users"
GROUPS_PATH_SEGMENT = "groups"
SCHEMAS_PATH_SEGMENT = "schemas"
TENANTS_PATH_SEGMENT = "tenants"
UI_PATH_SEGMENT = "ui"
UI_DOCUMENT_VIEWS_PATH_SEGMENT = "views"
UI_LIST_VIEWS_PATH_SEGMENT = "list_views"
META_PATH = "/{}".format(META_PATH_SEGMENT)
SCHEMAS_PATH = "{}/{}".format(META_PATH, SCHEMAS_PATH_SEGMENT)
USERS_PATH = "{}/{}".format(META_PATH, USERS_PATH_SEGMENT)
GROUPS_PATH = "{}/{}".format(META_PATH, GROUPS_PATH_SEGMENT)
TENANTS_PATH = "{}/{}".format(META_PATH, TENANTS_PATH_SEGMENT)
UI_PATH = "{}/{}".format(META_PATH, UI_PATH_SEGMENT)
UI_DOCUMENT_VIEWS_PATH = "{}/{}".format(UI_PATH, UI_DOCUMENT_VIEWS_PATH_SEGMENT)
UI_LIST_VIEWS_PATH = "{}/{}".format(UI_PATH, UI_LIST_VIEWS_PATH_SEGMENT)

ADMIN = "admin"
ADMINS = "admins"
ALL_PERMISSIONS = "rw"

# Document keys
TENANT_ID = "__tenant_id"
SCHEMA_ID = "__schema_id"
LOCAL_ACL = "__local_acl"
INHERIT_ACL = "__inherit_acl"
ACL = "__acl"
CREATED = "__created"
UPDATED = "__updated"
DOCUMENT_UUID = "__document_uuid"
SELF_UUID = "__self_uuid"
PARENT_UUID = "__parent_uuid"
PATH = "__path"
PATH_SEGMENT = "__path_segment"
PATH_HASH = "__path_hash"
IS_VERSION = "__is_version"
VERSION = "__version"
DATA = "__data"
FACETS = "__facets"

METADATA_FIELDS = [
    TENANT_ID,
    SCHEMA_ID,
    LOCAL_ACL,
    INHERIT_ACL,
    CREATED,
    UPDATED,
    DOCUMENT_UUID,
    SELF_UUID,
    PARENT_UUID,
    PATH_SEGMENT,
    IS_VERSION,
    VERSION,
    VIEW_CONFIG]

FACET_SHOW_IN_TREE = "__show_in_tree"
FACET_META = "__meta"

# The FDMS mapping of the schema document type
META_AND_FOLDER_FACETS = [FACET_SHOW_IN_TREE, FACET_META]
META_FACETS = [FACET_META]
# The FDMS mapping of the group document type
FOLDER_SCHEMA_PROPERTIES = {
}
# The FDMS mapping of the group document type
# The document containing the FDMS mapping of the schema document type
SCHEMA_SCHEMA_DOCUMENT = {
    "properties": {
        "properties": {"type": "json"},
        "id": {"alias": PATH_SEGMENT},
        "facets": {"type": "keyword"},
        "default_view_config": {"type": "keyword"},
    },
    "facets": META_FACETS
}
# The document containing the FDMS mapping of the folder document type
ROOT_SCHEMA_DOCUMENT = {
    "properties": {},
    "facets": META_AND_FOLDER_FACETS,
}
FOLDER_SCHEMA_DOCUMENT = {
    "properties": FOLDER_SCHEMA_PROPERTIES,
    "facets": META_AND_FOLDER_FACETS
}
USER_SCHEMA_DOCUMENT = {
    "properties": {
        "is_tenant_admin": {"type": "boolean"},
        "email": {"type": "email"},
        "id": {"alias": PATH_SEGMENT}
    },
    "facets": META_FACETS,
    "default_view_config": VIEW_USER_DOCUMENT
}
GROUP_SCHEMA_DOCUMENT = {
    "properties": {
        "users": {"type": "keyword", "list": True},
        "id": {"alias": PATH_SEGMENT}
    },
    "facets": META_FACETS,
    "default_view_config": VIEW_GROUP_DOCUMENT
}
TENANT_SCHEMA_DOCUMENT = {
    "properties": {"id": {"alias": PATH_SEGMENT}},
    "facets": META_FACETS
}
CONFIG_SCHEMA_DOCUMENT = {
    "properties": {"config": {"type": "json"}},
    "facets": META_FACETS
}

# Base properties
PROPERTIES_BASE = {
    # tenant_id: tenant id of this entry
    TENANT_ID: {"type": "keyword"},
    # schema_id: schema id of this entry
    SCHEMA_ID: {"type": "keyword"},
    # local_acl: acl for this enrry
    LOCAL_ACL: {"type": "keyword"},
    # inherited acl: true if this entry acl is based on the parent acls
    INHERIT_ACL: {"type": "boolean"},
    # acls: computed by es using  local_acl and parent_acl if inherit_acl is true
    ACL: {"type": "keyword"},
    # created: date of creation of this entry
    CREATED: {"type": "date"},
    # updated: date of the last update of this entry
    UPDATED: {"type": "date"},
    # document_uuid: uuid of the document (equals to self_uuid if this entry is a document)
    DOCUMENT_UUID: {"type": "keyword"},
    # self_uuid: uuid of this entry
    SELF_UUID: {"type": "keyword"},
    # parent_uuid: uuid of the parent document
    PARENT_UUID: {"type": "keyword"},
    # path: computed by es using parent path and path_segment
    PATH: {"type": "keyword"},
    # path_segment: unique identifier of a document in the brotherhood
    PATH_SEGMENT: {"type": "keyword"},
    # path_hash: computed by es using path and version, used as the id in elasticsearch for true uniqueness
    PATH_HASH: {"type": "keyword"},
    # is_version: is this entry a document or a version
    IS_VERSION: {"type": "boolean"},
    # version: version of the entry (is None for documents)
    VERSION: {"type": "keyword"},
    # view_config: configuration to display this document
    VIEW_CONFIG: {"type": "keyword"}
}
# Mapping of the data indexes
DATA_MAPPING = dict(PROPERTIES_BASE)
DATA_MAPPING.update({
    DATA:  {"type": "text", "index": False}
})
# Base mapping of the search indexes
SEARCH_MAPPING_BASE = dict(PROPERTIES_BASE)
SEARCH_MAPPING_BASE.update({
    FACETS:  {"type": "keyword"}
})

# pure FDMS properties in mappings (must be removed for creating an ES mapping)
FDMS_MAPPING_KEYS = ["alias", "list"]

# acl provided by the tenant service
TENANT_ACES = ["group:{}:".format(ADMINS)]


# base acl on all documents to enable all operations for the tenant and the administrators
ACL_BASE = [
    "group:{}:{}".format(ADMINS, ALL_PERMISSIONS),
]

ADMIN_CONTEXT = "admin_context"

DEFAULT_UI_CONFIG = {
    "views": {
        VIEW_DEFAULT: {
            "widgets": [
                {"auto": "__path_segment"},
                {"type": "separator"},
                {"type": "children", "widgets": [
                    {"auto": "__path_segment", "link": True}
                ]}
            ]
        },
        VIEW_GROUPS_FOLDER: {
            "widgets": [
                {"type": "children", "widgets": [
                    {"auto": "id", "link": True},
                    {"auto": "users", "icon": "user", "link": USERS_PATH + "/" + "{{model}}"},
                ]}
            ]
        },
        VIEW_USERS_FOLDER: {
            "widgets": [
                {"type": "children", "widgets": [
                    {"auto": "id", "link": True},
                ]}
            ]
        },
        VIEW_USER_DOCUMENT: {
            "widgets": [
                {"auto": "id"},
                {"auto": "email"},
                {"type": "list", 
                    "filter": {
                        SCHEMA_ID: GROUP_SCHEMA_ID,
                        "users": "{{doc.id}}"
                    },
                    "widgets": [
                    {"auto": "id", "icon": "users", "link": True, "label": "groups"},
                ]}
            ]
        },
        VIEW_GROUP_DOCUMENT: {
            "widgets": [
                { "auto": "id"},
                { "type": "list", 
                  "filter": {
                    SCHEMA_ID: USER_SCHEMA_ID,
                    "id": "{{doc.users}}"
                  },
                  "widgets": [
                  {"auto": "id", "icon": "user", "link": True, "label": "users"},
                ]}
            ]
        },
        VIEW_CONFIG_DOCUMENT: {
            "widgets": [
                {"auto": "__path_segment"},
                {"auto": "config", 
                 "structure_templates": {
                    "widgets": {
                        "type": "array"
                        "widgets": {
                            "json"
                        }
                    }
                 ],
                 "structure": {
                    "widgets": "widgets"
                 }},
            ]
        }
    }
}
