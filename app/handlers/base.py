# -*- coding: utf-8 -*-
import json
import pickle
from app import redis
from app.utils import get_cache, set_cache

from raven.contrib.tornado import SentryMixin
from tornado.web import RequestHandler
from tornado.escape import json_decode


class BaseHandler(SentryMixin, RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.result = {}
        self.data = {}
        self.set_header('Content-Type', 'application/json')

    def prepare(self):
        """只处理 JSON body"""
        if self.request.body:
            try:
                json_data = json_decode(self.request.body)
            except json.JSONDecodeError:
                self.write_json('无效的 JSON', 400)
            else:
                self.data = json_data

    def write_json(self, data, status_code=200):
        self.set_status(status_code)
        self.write(json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
        self.finish()

    def save_data(self, key, vaules):
        set_cache(key, vaules)

    def get_data(self, key):
        cache_data = get_cache(key)
        if cache_data:
            cache_data = {'ticket': cache_data, 'status_code': 201}

        return cache_data
