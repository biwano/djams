""" Contains the class managing tenants """
import logging
import json
from . import SchemaService
from .esService import EsService
from .documentService import DocumentService
from .documentHelpers import path
from .constants import (
    ROOT_SCHEMA_DOCUMENT,
    SCHEMA_SCHEMA_DOCUMENT,
    FOLDER_SCHEMA_DOCUMENT,
    USER_SCHEMA_DOCUMENT,
    GROUP_SCHEMA_DOCUMENT,
    TENANT_SCHEMA_DOCUMENT,
    CONFIG_SCHEMA_DOCUMENT,
    TENANT_MASTER_ID,
    SCHEMA_SCHEMA_ID,
    GROUP_SCHEMA_ID,
    USER_SCHEMA_ID,
    FOLDER_SCHEMA_ID,
    ROOT_SCHEMA_ID,
    TENANT_SCHEMA_ID,
    CONFIG_SCHEMA_ID,
    PATH_SEGMENT,
    META_PATH,
    SCHEMAS_PATH,
    USERS_PATH,
    GROUPS_PATH,
    TENANTS_PATH,
    META_PATH_SEGMENT,
    SCHEMAS_PATH_SEGMENT,
    USERS_PATH_SEGMENT,
    GROUPS_PATH_SEGMENT,
    TENANTS_PATH_SEGMENT,
    UI_PATH_SEGMENT,
    UI_PATH,
    UI_DOCUMENT_VIEWS_PATH,
    UI_LIST_VIEWS_PATH,
    UI_DOCUMENT_VIEWS_PATH_SEGMENT,
    UI_LIST_VIEWS_PATH_SEGMENT,
    DEFAULT_UI_CONFIG,
    ADMIN,
    VIEW_USERS_LIST,
    VIEW_GROUPS_LIST
)

class TenantService(object):
    """ Class managing tenants """
    def __init__(self, tenant_id, context):
        self.tenant_id = tenant_id
        self.es_service = EsService()
        self.context = context
        self.logger = logging.getLogger(type(self).__name__)


    def create(self, drop=False):
        """ Creates a tenant """
        # create data index
        self.logger.info("Creating tenant %s drop=%s", self.tenant_id, drop)
        self.es_service.create_data_index(self.tenant_id, drop)

        SchemaService(self.tenant_id, ROOT_SCHEMA_ID, self.context).register(ROOT_SCHEMA_DOCUMENT, drop=drop, persist=False)
        SchemaService(self.tenant_id, FOLDER_SCHEMA_ID, self.context).register(FOLDER_SCHEMA_DOCUMENT,  drop=drop, persist=False)
        
        document_service = DocumentService(self.tenant_id, self.context)
        # create root document
        document_service.create_root()
        
        # Create folders
        document_service.create(FOLDER_SCHEMA_ID, parent="/", path_segment=META_PATH_SEGMENT)
        document_service.create(FOLDER_SCHEMA_ID, parent=META_PATH, path_segment=SCHEMAS_PATH_SEGMENT)
        document_service.create(FOLDER_SCHEMA_ID, parent=META_PATH, path_segment=USERS_PATH_SEGMENT, view_config=VIEW_USERS_LIST)
        document_service.create(FOLDER_SCHEMA_ID, parent=META_PATH, path_segment=GROUPS_PATH_SEGMENT, view_config=VIEW_GROUPS_LIST)
        # UI
        document_service.create(FOLDER_SCHEMA_ID, parent=META_PATH, path_segment=UI_PATH_SEGMENT)
        document_service.create(FOLDER_SCHEMA_ID, parent=UI_PATH, path_segment=UI_DOCUMENT_VIEWS_PATH_SEGMENT)
        document_service.create(FOLDER_SCHEMA_ID, parent=UI_PATH, path_segment=UI_LIST_VIEWS_PATH_SEGMENT)

        # create base search indexes
        SchemaService(self.tenant_id, ROOT_SCHEMA_ID, self.context).register(ROOT_SCHEMA_DOCUMENT, drop=False)
        SchemaService(self.tenant_id, FOLDER_SCHEMA_ID, self.context).register(FOLDER_SCHEMA_DOCUMENT, drop=False)
        SchemaService(self.tenant_id, SCHEMA_SCHEMA_ID, self.context).register(SCHEMA_SCHEMA_DOCUMENT, drop=drop)
        SchemaService(self.tenant_id, USER_SCHEMA_ID, self.context).register(USER_SCHEMA_DOCUMENT, drop=drop)
        SchemaService(self.tenant_id, GROUP_SCHEMA_ID, self.context).register(GROUP_SCHEMA_DOCUMENT, drop=drop)
        SchemaService(self.tenant_id, CONFIG_SCHEMA_ID, self.context).register(CONFIG_SCHEMA_DOCUMENT, drop=drop)

        # create base users
        document_service.create(USER_SCHEMA_ID, parent=USERS_PATH, path_segment=ADMIN, data={
            "is_tenant_admin": True
            })
        # create base groups
        document_service.create(GROUP_SCHEMA_ID, parent=GROUPS_PATH, path_segment=ADMIN, data={
            "users": [ADMIN]
            })

        # create config (schemas)
        for key in DEFAULT_UI_CONFIG["views"]:
            config = DEFAULT_UI_CONFIG["views"][key]
            document_service.create(CONFIG_SCHEMA_ID, parent=UI_DOCUMENT_VIEWS_PATH, path_segment=key, data={
                "config": config
            })
        """
        for key in DEFAULT_UI_CONFIG["list_views"]:
            config = DEFAULT_UI_CONFIG["list_views"][key]
            document_service.create(CONFIG_SCHEMA_ID, parent=UI_LIST_VIEWS_PATH, path_segment=key, data={
                "config": config
            })
        """

        # Master tenant specifics
        if self.tenant_id == TENANT_MASTER_ID:
            SchemaService(self.tenant_id, TENANT_SCHEMA_ID, self.context).register(TENANT_SCHEMA_DOCUMENT, drop=drop)
            document_service.create(FOLDER_SCHEMA_ID, parent=META_PATH, path_segment=TENANTS_PATH_SEGMENT)


        # Register tenant in tenant master
        fdms_document_service = DocumentService(TENANT_MASTER_ID, self.context, refresh="wait_for")
        fdms_document_service.create(TENANT_SCHEMA_ID, parent=TENANTS_PATH, path_segment=self.tenant_id)

    def update(self, items):
        # TODO
        pass
        



    def delete(self, drop=False):
        """ Delete tenant """

        # Find all schemas
        document_service = DocumentService(self.tenant_id, self.context)
        schemas = document_service.search(query=None, schema_id=SCHEMA_SCHEMA_ID)

        # Delete all schemas
        for schema in schemas:
            SchemaService(self.tenant_id, schema[PATH_SEGMENT], self.context).delete()

        self.es_service.delete_data_index(self.tenant_id)

        # Unregister tenant in tenant master
        if self.tenant_id != TENANT_MASTER_ID:
            document_service = DocumentService(TENANT_MASTER_ID, self.context, refresh="wait_for")
            document_service.delete(path(TENANTS_PATH, self.tenant_id))
