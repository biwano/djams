""" Contains the class managing tenants """
from . import SchemaService
from .esService import EsService
from .documentService import DocumentService
from .constants import (DATA_MAPPING, 
SCHEMA_SCHEMA_DEFINITION, 
USER_SCHEMA_DEFINITION, 
GROUP_SCHEMA_DEFINITION,
TENANT_SCHEMA_DEFINITION,
TENANT_MASTER)

class TenantService(object):
    """ Class managing tenants """
    def __init__(self, tenant_id, context):
        self.tenant_id = tenant_id
        self.es_service = EsService()
        self.context = context
        

    def create(self, drop=False):
        """ Creates a tenant """
        index_name = EsService().get_data_index_name(self.tenant_id)
        EsService().create_index(index_name, DATA_MAPPING, drop)
        SchemaService(self.tenant_id, "schema", self.context).register(SCHEMA_SCHEMA_DEFINITION, drop)
        SchemaService(self.tenant_id, "user", self.context).register(USER_SCHEMA_DEFINITION, drop)
        SchemaService(self.tenant_id, "group", self.context).register(GROUP_SCHEMA_DEFINITION, drop)
        if self.tenant_id == TENANT_MASTER:
            SchemaService(self.tenant_id, "tenant", self.context).register(TENANT_SCHEMA_DEFINITION, drop)

        document_service = DocumentService(self.tenant_id, self.context)
        document_service.create("user", {
            "id": "admin",
            "is_tenant_admin": True
            })
        document_service.create("group", {
            "id": "admin",
            "users": ["admin"]
            })
        # Registering tenant in tenant master
        document_service = DocumentService(TENANT_MASTER, self.context)
        document_service.create("tenant", {
                "id": self.tenant_id,
                })
