""" Tenant views implementation """
from flask import request, abort
import fdms

class TenantsView(fdms.RequestHandler):
    def __init__(self):
        super().__init__()

    def create(self):
        """Creates a new realm"""
        body = self.get_body()
        tenant_id = body.get("tenant_id")
        if not tenant_id or "|" in tenant_id:
        	abort(400, "Invalid tenant ID")
        	return
        drop = body.get("drop")
        
        fdms.services.TenantService(tenant_id, self.context).create(drop)

        return self.send_success()

    def update(self, tenant_id):
        """Creates a new realm"""
        items = self.get_request_param_array("items")
        fdms.services.TenantService(tenant_id, self.context).update(items)
        return self.send_success()

        return self.send_success()
    def delete(self, tenant_id):
        fdms.services.TenantService(tenant_id, self.context).delete()
        return self.send_success()
