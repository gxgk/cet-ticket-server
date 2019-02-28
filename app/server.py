# -*- coding: utf-8 -*-
import os
import time
import requests
import zipfile
import json
from app.parse_pdf import parse_pdf
from app.utils import del_file
from threading import Thread

img_file = 'static/yzm.gif'
# 运行程序时，删除文件
del_file(img_file)


class CetTicket():
    threshold = 5 # 更换验证码的阙值
    code = None
    url = "http://cet-bm.neea.edu.cn/"
    _http = requests.session()

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

        # 开启心跳，用于保持会话有效
        t = Thread(target=self.heartbeat)
        t.start()

    def heartbeat(self):
        ''' 保持会话长期有效 '''
        while True:
            time.sleep(60)
            try:
                self.update_session(self.code)
            except:
                time.sleep(5)
                self.update_session(self.code)


    def get_code(self):
        if not os.path.exists(img_file):
            res = self._http.get(self.url + "/Home/VerifyCodeImg")
            with open(img_file, 'wb') as f:
                f.write(res.content)

        return self.code

    def update_session(self, code=None):
        ''' 更新会话 '''
        if code and not self.code:
            self.code = code
        data = {'real_name': 'XXXXX', "id_card": "XXXXXX", "id_type_code": 1, "province_code":44}
        result = self.get_ticket(**data)
        return result

    def get_ticket(self, real_name, id_card, province_code, id_type_code, code=None):
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
        res = self._http.post(self.url + "/Home/ToQuickPrintTestTicket", data=data)
        msg = res.json()['Message']
        if msg[:7] == '[{"SID"':
            # 获取考号
            msg = json.loads(msg)[0]
            sid = msg["SID"]
            ticket = self._get_report(sid)
            result = {"ticket": ticket, "status": 200}
            self.threshold = 5

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
                self.get_code()
            self.code = None
            result = {"msg": msg, "status": 400}
        else:
            # 其他问题
            result = {"msg": msg, "status": 201}
            self.threshold = 5
        return result

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