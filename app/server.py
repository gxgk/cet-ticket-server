# -*- coding: utf-8 -*-
import os
import time
import asyncio
import requests_async
import zipfile
import json
from app.parse_pdf import parse_pdf
from app.utils import del_file, get_cache, set_cache
from threading import Thread

img_file = 'static/yzm.gif'


class CetTicket():
    code = None
    threshold = 5  # 更换验证码的阙值
    url = "http://cet-bm.neea.edu.cn/"
    _http = requests_async.Session()

    def __init__(self):
        ''' 创建一个请求 '''
        self._http.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/62.0.3202.89 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.url
        })

        pid = os.fork()
        if pid == 0:
            self.start_heartbeat()

    def start_heartbeat(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._keep_session())
        loop.close()

    async def _keep_session(self):
        ''' 保持会话 '''
        data = {'real_name': 'XXXXX', "id_card": "XXXXXX", "id_type_code": 1, "province_code": 44}

        while True:
            await asyncio.sleep(5)
            result = await self.get_ticket(**data)
            print("update", result)

    def save_session(self):
        cookie = self._http.cookies.get_dict()
        set_cache("session", {"yzm_code": self.code, "cookie": cookie})

    async def load_session(self):
        cache_data = get_cache("session")
        if cache_data:
            self.code = cache_data["yzm_code"]
            self._http.cookies.update(cache_data['cookie'])

    def _get_report(self, sid):
        ''' 解析准考证文件 pdf，提取准考证号码 '''
        res = self._http.get(f"{self.url}/Home/DownTestTicket?SID={sid}")
        with open(sid, "wb") as f:
            f.write(res.content)

        with zipfile.ZipFile(sid, "r") as zipf:
            for names in zipf.namelist():
                # print(names.encode('cp437').decode('gbk'))
                pdf_file = f"data_file/cet_file/{names.encode('cp437').decode('gbk')}"
                data = zipf.read(names)
                with open(pdf_file, "wb") as f:
                    f.write(data)
                    os.remove(sid)
                return parse_pdf(pdf_file)

    async def get_code(self):
        await self.load_session()
        if not os.path.exists(img_file):
            res = await self._http.get(self.url + "/Home/VerifyCodeImg")
            with open(img_file, 'wb') as f:
                f.write(res.content)

        return self.code

    async def get_ticket(self, real_name, id_card, province_code, id_type_code, code=None):
        await self.load_session()

        ''' 获取考号 '''
        if not self.code:
            self.threshold -= 1
            self.code = code

        data = {
            "provinceCode": province_code,
            "IDTypeCode": id_type_code,
            "IDNumber": id_card,
            "Name": real_name,
            "verificationCode": self.code
        }
        res = await self._http.post(self.url + "/Home/ToQuickPrintTestTicket", data=data)
        msg = res.json()['Message']

        if msg[:7] == '[{"SID"':
            # 获取考号
            msg = json.loads(msg)[0]
            sid = msg["SID"]
            if sid:
                ticket = self._get_report(sid)
                result = {"ticket": ticket, "status": 200}
                self.threshold = 5
            else:
                result = {"msg": msg['Memo'], "status": 400}

        elif msg in ['验证码已超时失效，请重新输入。', '验证码错误', 'SQL语句存在风险，禁止执行！',
                     'Object reference not set to an instance of an object.']:
            # 验证码问题
            if msg == 'SQL语句存在风险，禁止执行！':
                msg = '参数有误'
            elif msg == 'Object reference not set to an instance of an object.':
                msg = '请输入验证码'
            elif self.code and self.threshold == 0 or msg == '验证码已超时失效，请重新输入。':
                del_file(img_file)
                self.threshold = 5
                await self.get_code()
            self.code = None
            result = {"msg": msg, "status": 400}
        else:
            # 其他问题
            result = {"msg": msg, "status": 201}
            self.threshold = 5

        self.save_session()

        return result
