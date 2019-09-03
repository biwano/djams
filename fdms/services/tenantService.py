""" Contains the class managing tenants """
from . import SchemaService
from .esService import EsService
from .documentService import DocumentService
from .constants import (
    SCHEMA_SCHEMA_DEFINITION,
    FOLDER_SCHEMA_DEFINITION,
    USER_SCHEMA_DEFINITION,
    GROUP_SCHEMA_DEFINITION,
    TENANT_SCHEMA_DEFINITION,
    TENANT_MASTER_ID,
    SCHEMA_SCHEMA_ID,
    GROUP_SCHEMA_ID,
    USER_SCHEMA_ID,
    FOLDER_SCHEMA_ID,
    ROOT_SCHEMA_ID,
    TENANT_SCHEMA_ID,
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
    ADMIN
    )

class TenantService(object):
    """ Class managing tenants """
    def __init__(self, tenant_id, context):
        self.tenant_id = tenant_id
        self.es_service = EsService()
        self.context = context
        

    def create(self, drop=False):
        """ Creates a tenant """
        # create data index
        self.es_service.create_data_index(self.tenant_id, drop)

        SchemaService(self.tenant_id, ROOT_SCHEMA_ID, self.context).register(SCHEMA_SCHEMA_DEFINITION, drop, persist=False)
        
        document_service = DocumentService(self.tenant_id, self.context)
        # create root document
        root = document_service.create_root()

        # create base search indexes
        SchemaService(self.tenant_id, SCHEMA_SCHEMA_ID, self.context).register(SCHEMA_SCHEMA_DEFINITION, drop)
        SchemaService(self.tenant_id, ROOT_SCHEMA_ID, self.context).register(SCHEMA_SCHEMA_DEFINITION, drop=False)
        SchemaService(self.tenant_id, FOLDER_SCHEMA_ID, self.context).register(FOLDER_SCHEMA_DEFINITION, drop)
        SchemaService(self.tenant_id, USER_SCHEMA_ID, self.context).register(USER_SCHEMA_DEFINITION, drop)
        SchemaService(self.tenant_id, GROUP_SCHEMA_ID, self.context).register(GROUP_SCHEMA_DEFINITION, drop)

        # Create folders
        document_service.create(FOLDER_SCHEMA_ID, parent="/", path_segment=META_PATH_SEGMENT)
        document_service.create(FOLDER_SCHEMA_ID, parent=META_PATH, path_segment=USERS_PATH_SEGMENT)
        document_service.create(FOLDER_SCHEMA_ID, parent=META_PATH, path_segment=GROUPS_PATH_SEGMENT)
        # create base users
        document_service.create(USER_SCHEMA_ID, parent=USERS_PATH, path_segment=ADMIN, data={
            "is_tenant_admin": True
            })
        # create base groups
        document_service.create(GROUP_SCHEMA_ID, parent=GROUPS_PATH, path_segment=ADMIN, data={
            "users": [ADMIN]
            })
        # MAster tenant specifics
        if self.tenant_id == TENANT_MASTER_ID:
            SchemaService(self.tenant_id, TENANT_SCHEMA_ID, self.context).register(TENANT_SCHEMA_DEFINITION, drop)
            document_service.create(FOLDER_SCHEMA_ID, parent=META_PATH, path_segment=TENANTS_PATH_SEGMENT)


        # Register tenant in tenant master
        fdms_document_service = DocumentService(TENANT_MASTER_ID, self.context, refresh="wait_for")
        fdms_document_service.create(TENANT_SCHEMA_ID, parent=TENANTS_PATH, path_segment=self.tenant_id)

    def delete(self, drop=False):
        """ Delete tenant """

        # Find all schemas
        document_service = DocumentService(self.tenant_id, self.context)
        schemas = document_service.search(SCHEMA_SCHEMA_ID)

        # Delete all schemas
        for schema in schemas:
            SchemaService(self.tenant_id, schema["path_segment"], self.context).delete()

        self.es_service.delete_data_index(self.tenant_id)

        # Unregister tenant in tenant master

        document_service = DocumentService(TENANT_MASTER_ID, self.context, refresh="wait_for")
        document_service.delete_child_by_id("/", self.tenant_id)
