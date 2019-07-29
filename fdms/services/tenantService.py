""" Contains the class managing tenants """
from . import SchemaService
from .esService import es_service
from .constants import DATA_MAPPING, SCHEMA_SCHEMA_DEFINITION, TENANT_ACES

class TenantService(object):
    """ Class managing tenants """
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id

    def create(self, drop=False):
        """ Creates a tenant """
        index_name = es_service.get_data_index_name(self.tenant_id)
        es_service.create_index(index_name, DATA_MAPPING, drop)
        SchemaService(self.tenant_id, "schema", TENANT_ACES).register(SCHEMA_SCHEMA_DEFINITION, drop)
