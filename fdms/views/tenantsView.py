""" Tenant views implementation """
import fdms

class TenantsView(fdms.RequestHandler):
    def create(self):
        """Creates a new realm"""
        super().__init__()
        body = self.get_body()
        tenant_id = body.get("tenant_id")
        drop = body.get("drop")
        
        fdms.services.TenantService(tenant_id, self.context).create(drop)

        return self.send_success(body)
