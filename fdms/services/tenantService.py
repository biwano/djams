from .. import model
from . import SchemaService
from .esService import es_service
from .constants import DATA_MAPPING, SCHEMA_SCHEMA_DEFINITION

class TenantService():
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
    
    def create(self, drop=False):
        index_name = es_service.getDataIndexName(self.tenant_id)
        es_service.createIndex(index_name, DATA_MAPPING, drop)
        SchemaService(self.tenant_id, "schema").register(SCHEMA_SCHEMA_DEFINITION, drop)

