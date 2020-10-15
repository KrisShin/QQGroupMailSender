import logging
from time import sleep
from random import random, randint
from tkinter import messagebox
import json
import os

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("QGM.log", encoding='utf-8')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# DATAPATH = os.path.join(os.environ['APPDATA'], 'misc', 'QGM')
DATAPATH = '.'

if not os.path.exists(DATAPATH):
    os.makedirs(DATAPATH, 777)

TUTORIAL = '''请提前安装chrome浏览器并下载对应版本的chromedriver并放入当前文件夹
驱动下载地址在本程序左上角
发送者的邮箱和授权码请以json格式放入当前文件夹

---account.json
{
    "qq": [
        {
            "email": "xxxxxxxx@qq.com",
            "auth": "xxxxxxxxxxxx"
        }
    ],
    "163": [
        {
            "email": "xxxxxxxx@163.com",
            "auth": "xxxxxxxxxxxx"
        }
    ],
    "126": [
        {
            "email": "xxxxxxxx@126.com",
            "auth": "xxxxxxxxxxxx"
        }
    ],
}
'''


def save_txt(data, filePath, mode='w'):
    path = os.path.join(DATAPATH, filePath)
    dirc = os.path.split(path)[0]
    if not os.path.exists(dirc):
        os.makedirs(dirc, 777)
    if not isinstance(data, str):
        data = json.dumps(data)
    with open(path, mode) as fs:
        fs.write(data)
    return True


def dialogMsg(msg='', m='info'):
    if m == 'warn':
        messagebox.showwarning('警告', msg)
    elif m == 'err':
        messagebox.showerror('错误', msg)
    elif m == 't':
        messagebox.showinfo('使用说明', TUTORIAL)
    else:
        messagebox.showinfo('提示', msg)


def logT(msg, m='info'):
    if m == 'warn':
        logger.warning(msg)
    elif m == 'err':
        logger.error(msg)
    else:
        logger.info(msg)


def randSleep(start, end):
    '''random sleep start seconds to end seconds'''
    sleep(random()*(end-start) + start)


if __name__ == "__main__":
    logT('wori')
    logT('wori warning', 'warn')
    logT('wori error', 'err')
