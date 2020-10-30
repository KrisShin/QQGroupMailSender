import logging
from time import sleep
from random import random, randint
from tkinter import messagebox
import json
import os
import re
import shutil


WINDOW_WIDTH = 680  # 窗口大小
WINDOW_HEIGHT = 470
WINDOW_X = 0  # 窗口距中心点偏移值
WINDOW_Y = 0
NUMBER = 5  # 一封邮件发送的人数
UPDATE_DATE = '2020-10-28'
DATAPATH = os.path.join(os.environ['APPDATA'], 'QGM')
# DATAPATH = '.'
GROUPPATH = os.path.join(DATAPATH, 'groups')
CONFPATH = os.path.join(DATAPATH, 'localconf')

CONFIGS = {
    'gids': [],
    'new': True,
    'crawlingGid': '',
    'newCrawled': [],
    'crawledGids': [],
    'sendingGid': '',
    'sendGids': [],
    'updateDate': ''
}


TUTORIAL = '''请提前安装chrome浏览器并下载对应版本的chromedriver并放入当前文件夹
驱动下载地址在本程序左上角
发送者的邮箱和授权码请以json格式放入当前文件夹
发送邮件之前需要选择要发送的群号, 左侧列表可以使用ctrl+A全选
点击>>按钮导入, 如果选择错误双击右侧的群号可以删除
- 10.28
  > 增加本地缓存
  > 优化程序逻辑, 提高易用性
'''


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("QGM.log", encoding='utf-8')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


if not os.path.exists(GROUPPATH):
    os.makedirs(GROUPPATH, 777)

if not os.path.exists(CONFPATH):
    with open(CONFPATH, 'w') as fc:
        fc.write(json.dumps(CONFIGS))
else:
    with open(CONFPATH, 'r') as fc:
        CONFIGS = json.loads(fc.read())
