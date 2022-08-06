import json
import requests
import setting
from message import DingTalkService


class DingTalkError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


robot_access_token = {
    "monitor": setting.ding_talk_monitor_robot_access_token,
    "strategy": setting.ding_talk_strategy_robot_access_token,
}
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token="


def get_webhook_url(robot_type="monitor"):
    if robot_type in robot_access_token:
        return webhook_url + robot_access_token[robot_type]
    raise DingTalkError(f"未找到机器人类型 {robot_type}")


def get_access_token():
    _appkey = setting.ding_talk_app_key
    _appsecret = setting.ding_talk_app_secret

    url = 'https://oapi.dingtalk.com/gettoken?appkey=%s&appsecret=%s' % (_appkey, _appsecret)

    headers = {
        'Content-Type': "application/x-www-form-urlencoded"
    }
    data = {'appkey': _appkey,
            'appsecret': _appsecret}
    r = requests.request('GET', url, data=data, headers=headers)
    access_token = r.json()["access_token"]

    print(access_token)
    return access_token


def send_message(robot_type='monitor'):
    url = get_webhook_url(robot_type)
    headers = {'content-type': 'application/json',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    post_data = {
        "msgtype": "text",

        "text": {
            "content": "通知: 测试信息."
        },
        "at": {
            "atUserIds": ["10093530"],
        }
    }
    r = requests.post(url, headers=headers, data=json.dumps(post_data))
    print(r.content)


def send_text_to_dingtalk(message: str):
    DingTalkService().send_text(message)


def get_media_id():
    access_token = get_access_token()
    # 获取要推送文件的路径
    # path = os.getcwd()
    # file = os.path.join(path, '文件名')
    file = r'/mpf/3.png'
    url = 'https://oapi.dingtalk.com/media/upload?access_token=%s&type=file' % access_token
    files = {'media': open(file, 'rb')}
    data = {'access_token': access_token,
            'type': 'file'}
    response = requests.post(url, files=files, data=data)
    json = response.json()
    print(json)
    return json["media_id"]


def send_file():
    access_token = get_access_token()
    media_id = get_media_id()
    chatid = setting.ding_talk_chat_id
    url = 'https://oapi.dingtalk.com/chat/send?access_token=' + access_token
    header = {
        'Content-Type': 'application/json'
    }
    data = {'access_token': access_token,
            'chatid': chatid,
            'msg': {
                'msgtype': 'file',
                'file': {'media_id': media_id}
            }}
    r = requests.request('POST', url, data=json.dumps(data), headers=header)
    print(r.json())


if __name__ == '__main__':
    send_file()
