# -*- coding: utf-8 -*-
import os
from redis import Redis
from redis import StrictRedis
from app.settings import REDIS_URL

redis = StrictRedis.from_url(REDIS_URL)

from app.server import CetTicket

cet_ticket = CetTicket()
