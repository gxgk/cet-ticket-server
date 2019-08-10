# -*- coding: utf-8 -*-
import os
import asyncio
import httpx
import zipfile
import json
from app.parse_pdf import parse_pdf
from app.utils import del_file, get_cache, set_cache

img_file = 'static/yzm.gif'

_http = httpx.AsyncClient()


class CetTicket():
    code = None
    threshold = 5  # 更换验证码的阙值
    url = "http://cet-bm.neea.edu.cn/"

    def __init__(self):
        ''' 创建一个请求 '''
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
            await asyncio.sleep(10)
            result = await self.get_ticket(**data, refresh_session=False)

    def save_session(self):
        cookie = dict(_http.cookies)
        set_cache("session", {"yzm_code": self.code, "cookie": cookie})

    def get_cookies(self):
        cache_data = get_cache("session")
        cookies = httpx.Cookies()
        if cache_data:
            self.code = cache_data["yzm_code"]
            for index in cache_data["cookie"]:
                cookies.set(index, cache_data["cookie"][index])
        return cookies

    async def _get_report(self, sid):
        ''' 解析准考证文件 pdf，提取准考证号码 '''
        res = await _http.get(f"{self.url}/Home/DownTestTicket?SID={sid}")
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
        cookies = self.get_cookies()
        if not os.path.exists(img_file):
            res = await _http.get(self.url + "/Home/VerifyCodeImg", cookies=cookies)
            with open(img_file, 'wb') as f:
                f.write(res.content)

        return self.code

    async def get_ticket(self, real_name, id_card, province_code, id_type_code, code=None, refresh_session=True):
        cookies = self.get_cookies()

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
        res = await _http.post(self.url + "/Home/ToQuickPrintTestTicket", data=data, cookies=cookies)
        msg = res.json()['Message']

        if msg[:7] == '[{"SID"':
            # 获取考号
            msg = json.loads(msg)[0]
            sid = msg["SID"]
            if sid:
                ticket = await self._get_report(sid)
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
        if refresh_session:
            self.save_session()

        return result
