from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import logging
from flask import current_app
from pprint import pformat

def get_cache():
	return current_app.extensions["cache"]

class FlaskCache(object):
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(type(self).__name__)
        self.init_app(app)

    def init_app(self, app):
        self.logger.info("Initializing Cache %s", pformat(app.config['CACHE']))
        cachemanager = CacheManager(**parse_cache_config_options(app.config['CACHE']))
        cache = cachemanager.get_cache('cache')
        app.extensions['cache'] = cache