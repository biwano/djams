""" Tenant views implementation """
from flask import request
import fdms
import copy

class DocumentsView(fdms.RequestHandler):
    def __init__(self):
        super().__init__()
        self.tenant_id = self.get_request_tenant_id()
        self.schema_id = self.get_request_schema_id()
        self.document_service = fdms.services.DocumentService(self.tenant_id, self.context)
    """
    def search(self):
        docs = fdms.services.DocumentService(self.tenant_id, self.context
                                             ).search(self.schema_id)
        return self.send(docs)
    """

    def filter(self):
        """Searches a document"""
        filt = []
        for arg in request.args:
            filt.append({"term": {arg: request.args[arg]}})
        docs = self.document_service.search(query={"bool": {"filter": filt}},
                                                      schema_id=self.schema_id)
        return self.send(docs)

    def get(self, doc):
        """Get a document"""
        path = fdms.path(doc)
        modifiers = self.get_request_param_array("__modifiers")
        
        with_permissions = True if "with_permissions" in modifiers else False
        if "children" in modifiers:
            filt = {}
            for i in request.args:
                filt[i] = request.args[i]
            del filt["__modifiers"]
            result = self.document_service.search_children(path, filt, with_permissions=with_permissions)
        else:
            result = self.document_service.get_by_path(path, with_permissions=with_permissions)

        return self.send(result)

    def update(self, doc):
        """Creates a new realm"""
        path = fdms.path(doc)
        body = self.get_body()
        doc = self.document_service.update(path, body)
        return self.send(doc)
    """
    def create(self):
       
        body = self.get_body()
        docs = fdms.services.DocumentService(self.tenant_id, self.context).create(self.schema_id, body)
        return self.send(docs)
    """
