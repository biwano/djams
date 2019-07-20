from flask import request
import uuid

def ensure_request_attr_container():
	if (not hasattr(request, "flaskdms")):
		setattr(request, "flaskdms", {})


def set_request_attr(key, value):
	ensure_request_attr_container()
	request.flaskdms[key] = value

def get_request_attr(key):
	ensure_request_attr_container()
	return request.flaskdms[key]

def get_uuid():
	return uuid.uuid4().hex
