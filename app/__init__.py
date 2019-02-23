# -*- coding: utf-8 -*-
import os
from redis import Redis


REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
redis = Redis(host=REDIS_HOST)

from app.server import CetTicket

cet_ticket = CetTicket()
