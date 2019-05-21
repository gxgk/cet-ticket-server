# -*- coding: utf-8 -*-
from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado.concurrent import run_on_executor
from app import cet_ticket

from app.handlers.base import BaseHandler
from app.settings import logger



class Index(RequestHandler):

    async def get(self):
        code = await cet_ticket.get_code()
        self.render('index.html', code=code)


class GetTicket(BaseHandler):
    ''' 获取准考号 '''

    async def async_get_ticket(self):
        result = self.get_data(self.data['id_card'])
        if not result:
            result = await cet_ticket.get_ticket(**self.data)
        return result

    async def post(self):
        self.result = await self.async_get_ticket()
        self.write_json(self.result)

    def on_finish(self):
        if self.result.get("status") == 200:
            # 保存考号
            self.save_data(self.data['id_card'], self.result['ticket'])
        logger.info("身份证号码：%s, %s", self.data['id_card'], str(self.result))
