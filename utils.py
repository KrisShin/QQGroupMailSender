import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


TUTORIAL = '''请提前安装chrome浏览器并下载对应版本的chromedriver并放入当前文件夹
驱动下载地址在本程序左上角
发送者的邮箱和授权码请以文本文件形式放入当前文件夹
QQ邮箱放入qq.txt内容为:
12345678@qq.com&yourqqmailauthcode
12345678@qq.com&yourqqmailauthcode
'''


def save_txt(data, filePath, mode='w'):
    with open(filePath, mode) as fs:
        fs.write(data)
    return 200


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


if __name__ == "__main__":
    logT('wori')
    logT('wori warning', 'warn')
    logT('wori error', 'err')
