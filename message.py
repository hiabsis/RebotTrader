import json
import hashlib
import base64
import hmac
import time
import requests
from urllib.parse import quote_plus

from setting import ding_talk_monitor_robot_secret, ding_talk_monitor_robot_access_token


class DingTalkService:
    def __init__(self):
        self.timestamp = str(round(time.time() * 1000))
        self.URL = "https://oapi.dingtalk.com/robot/send"
        self.headers = {'Content-Type': 'application/json'}
        secret = ding_talk_monitor_robot_secret
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(self.timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        self.sign = quote_plus(base64.b64encode(hmac_code))
        self.params = {'access_token': ding_talk_monitor_robot_access_token, "sign": self.sign}

    def send_text(self, content):
        """
        发送文本
        @param content: str, 文本内容
        """
        data = {"msgtype": "text", "text": {"content": content}}
        self.params["timestamp"] = self.timestamp
        return requests.post(
            url=self.URL,
            data=json.dumps(data),
            params=self.params,
            headers=self.headers
        )
