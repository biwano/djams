""" Tenant views implementation """
import fdms

class DocumentsView(fdms.RequestHandler):
    def __init__(self):
        super().__init__()
        self.tenant_id = self.get_request_tenant_id()
        self.schema_id = self.get_request_schema_id()

    def search(self):
        """Searches a document"""
        docs = fdms.services.DocumentService(self.tenant_id, self.context).search(self.schema_id)
        return self.send(docs)

    def create(self):
        """Creates a new realm"""
        body = self.get_body()
        docs = fdms.services.DocumentService(self.tenant_id, self.context).create(self.schema_id, body)
        return self.send(docs)
