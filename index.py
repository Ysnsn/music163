# coding: utf-8
import requests
import json
import re
from user import User
from wecom import WeComtAlert


def start():
    with open('./config.json', 'r', encoding='utf-8') as f:
        config = json.loads(re.sub(r'\/\*[\s\S]*?\/', '', f.read()))
    setting = config['setting']

    user_count = 0

    SCKEYs = {}
    Skeys = {}
    pushToken = {}

    for user_config in config['users']:
        user_count += 1

        user_setting = setting
        if "setting" in user_config:
            for key in user_config['setting']:
                user_setting[key] = user_config['setting'][key]

        user = User()
        user.setUser(username=user_config['username'], password=user_config['password'],
                     isMd5=user_config['md5'], user_setting=user_setting, No=user_count, ip=user_config['X-Real-IP'])
        if user.isLogined:
            user.userInfo()

            if user_setting['follow']:
                user.follow()

            if user_setting['sign']:
                user.sign()
            if user.userType == 4:
                user.musician_task()

            task_on = False
            tasks = user_setting['yunbei_task']
            for task in user_setting['yunbei_task']:
                task_on = task_on or tasks[task]['enable']
            if task_on:
                user.yunbei_task()

            user.get_yunbei()

            if user.vipType == 11:
                user.vip_task()

            if user_setting['daka']['enable']:
                user.daka()

            if user_setting['other']['play_playlists']['enable']:
                user.play_playlists()

        user.msg = user.msg.strip()
        sckey = user_setting['serverChan']['SCKEY']
        if user_setting['serverChan']['enable'] and sckey != '':
            if sckey in SCKEYs:
                SCKEYs[sckey]['msg'] += user.msg
            else:
                SCKEYs[sckey] = {'title': user.title, 'msg': user.msg}

        skey = user_setting['CoolPush']['Skey']
        if user_setting['CoolPush']['enable'] and skey != '':
            if skey in Skeys:
                Skeys[skey]['msg'] += user.msg
            else:
                Skeys[skey] = {
                    'title': user.title, 'method': user_setting['CoolPush']['method'], 'msg': user.msg}

        pushtoken = user_setting['pushPlus']['pushToken']
        if user_setting['pushPlus']['enable'] and pushtoken != '':
            if pushtoken in pushToken:
                pushToken[pushtoken]['msg'] += user.msg
            else:
                pushToken[pushtoken] = {'title': user.title, 'msg': user.msg}

        if user_setting['WeCom']['enable'] and user_setting['WeCom']['corpid'] != "" and user_setting['WeCom']['secret'] != "" and user_setting['WeCom']['agentid'] != "":
            alert = WeComtAlert(
                user_setting['WeCom']['corpid'], user_setting['WeCom']['secret'], user_setting['WeCom']['agentid'])
            alert.send_msg(user_setting['WeCom']['userid'], user_setting['WeCom']['msgtype'],
                           user.msg, "网易云音乐打卡", 'https://music.163.com/#/user/home?id='+str(user.uid))

    for sckey in SCKEYs:
        serverChan_url = 'http://sc.ftqq.com/'+sckey+'.send'
        requests.post(serverChan_url, data={
                      "text": SCKEYs[sckey]['title'], "desp": SCKEYs[sckey]['msg']})

    for skey in Skeys:
        for method in Skeys[skey]['method']:
            CoolPush_url = "https://push.xuthus.cc/{}/{}".format(method, skey)
            if method == "email":
                requests.post(CoolPush_url, data={
                              "t": Skeys[skey]['title'], "c": Skeys[skey]['msg']})
            else:
                requests.get(CoolPush_url, params={"c": Skeys[skey]['msg']})

    # Pushplus推送
    for pushtoken in pushToken:
        push_url = 'http://www.pushplus.plus/send'
        data = {
            "token": pushtoken,
            "title": pushToken[pushtoken]['title'],
            "content": pushToken[pushtoken]['msg']
        }
        body = json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        requests.post(push_url, data=body, headers=headers)


def main_handler(event, context):
    return start()


if __name__ == '__main__':
    start()
