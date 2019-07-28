import json
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
from sqlalchemy.ext.declarative import DeclarativeMeta

db = SQLAlchemy()
es = Elasticsearch()

"""
class Tenant(db.Model):
    uuid = db.Column(db.String(64), primary_key=True)
    id = db.Column(db.String(16), primary_key=False, index=True)
    label = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<Tenant %r>' % self.label
"""

class Document(db.Model):
    tenant_id = db.Column(db.String(64), primary_key=True)
    schema_id = db.Column(db.String(64), primary_key=True)
    key = db.Column(db.String(64), primary_key=True)
    version = db.Column(db.String(64), primary_key=True)
    document_version_uuid = db.Column(db.String(64), index=True)
    document_uuid = db.Column(db.String(64), index=True)
    parent_uuid = db.Column(db.String(64), index=True)
    local_acl = db.Column(db.String())
    is_acl_inherited = db.Column(db.Integer())
    is_version = db.Column(db.Integer())
    created = db.Column(db.DateTime())
    updated = db.Column(db.DateTime())
    data = db.Column(db.String())

    
    def __repr__(self):
        return '<Document %r>' % self.label

class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)