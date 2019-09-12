""" Config views implementation """
import fdms
from fdms.services.constants import SEARCH_MAPPING_BASE


class ConfigView(fdms.RequestHandler):
    def __init__(self):
        super().__init__()


    def get(self):
        """Get a document"""
        return self.send({"base_properties": SEARCH_MAPPING_BASE})

