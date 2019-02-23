# -*- coding: utf-8 -*-
from app.handlers import Index, GetTicket

url_patterns = [
    (r'/', Index),
    (r'/get_ticket', GetTicket),
]
