""" Tenant views implementation """
from flask import request
import fdms
import copy

class DocumentsView(fdms.RequestHandler):
    def __init__(self):
        super().__init__()
        self.tenant_id = self.get_request_tenant_id()
        self.schema_id = self.get_request_schema_id()
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
        docs = fdms.services.DocumentService(self.tenant_id, self.context
                                             ).search(query={"bool": {"filter": filt}},
                                                      schema_id=self.schema_id)
        return self.send(docs)

    def get(self, doc):
        """Get a document"""
        path = fdms.path(doc)
        modifiers = request.args.get('__modifiers')
        if modifiers is not None:
            modifiers = modifiers.split(",")
        else:
            modifiers = []
        print(modifiers)
        document_service = fdms.services.DocumentService(self.tenant_id, self.context)
        if "children" in modifiers:
            filt = {}
            for i in request.args:
                filt[i] = request.args[i]
            del filt["__modifiers"]
            result = document_service.search_children(path, filt)
        else:
            result = document_service.get_by_path(path)
        return self.send(result)

    def create(self):
        """Creates a new realm"""
        body = self.get_body()
        docs = fdms.services.DocumentService(self.tenant_id, self.context).create(self.schema_id, body)
        return self.send(docs)
