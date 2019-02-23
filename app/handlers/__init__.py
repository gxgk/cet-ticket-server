# -*- coding: utf-8 -*-
from tornado.web import RequestHandler
from app import cet_ticket

from app.handlers.base import BaseHandler


class Index(RequestHandler):

    def get(self):
        code = cet_ticket.get_code()
        self.render('index.html', code=code)


class GetTicket(BaseHandler):
    ''' 获取准考号 '''

    async def async_get_ticket(self):
        result = self.get_data(self.data['id_card'])
        if not result:
            result = cet_ticket.get_ticket(**self.data)
        return result

    async def post(self):
        self.result = await self.async_get_ticket()
        self.write_json(self.result)

    def on_finish(self):
        if self.result and self.result.get("status") == 200 and self.result.get('ticket'):
            # 保存考号
            self.save_data(self.data['id_card'], self.result['ticket'])