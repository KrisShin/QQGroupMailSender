import time
import os
import re
from math import ceil
import platform

from selenium import webdriver

from utils import save_txt, logT, randSleep, randint, sleep, DATAPATH


DRIVERPATH = r'.\chromedriver.exe' if platform.system(
) == 'Windows' else r'./chromedriver'


def _parseMails(driver):
    html = driver.page_source  # 获取源码
    reg = re.compile(r'<td>\s*?([1-9]\d{4,11})\s*?</td>')
    qqs = re.findall(reg, html)
    n = ceil(len(qqs)/10)
    mails = []
    for i in range(n):
        mails.append([f'{qq}@qq.com' for qq in qqs[i*10:(i+1)*10]])
    return mails


def _parse_group(driver):
    html = driver.page_source
    reg = re.compile(r'<li title=".*?" data-id="([1-9]\d{4,12})"')
    group_ids = re.findall(reg, html)
    return group_ids


def _scroll2foot(driver):
    '''
    下拉界面
    '''
    js = "var q=document.documentElement.scrollTop=100000"
    max_n = 0
    while max_n < len(driver.page_source):
        max_n = len(driver.page_source)
        driver.execute_script(js)
        randSleep(0.3, 3)
    return 1


def _launchChromeDriver():
    try:
        driver = webdriver.Chrome(executable_path=DRIVERPATH)
        return driver
    except:
        logT('请确认驱动版本以及是否在本文件夹内', 'err')
        return False


def crawlQQNum(group_ids):
    logT('开始获取所有QQ号')
    driver = _launchChromeDriver()
    if not driver:
        return False
    count = randint(3, 5)
    logT(f'本次将爬取{count}个群')
    mails = {}
    for gid in group_ids:
        groupDir = os.path.join(DATAPATH, 'groups')
        if os.path.exists(groupDir) and gid in os.listdir(groupDir):
            continue
        gurl = f'https://qun.qq.com/member.html#gid={gid}'
        driver.get(url=gurl)
        driver.refresh()
        randSleep(10, 12)  # wating to scan
        _scroll2foot(driver)
        mails[gid] = _parseMails(driver)  # 保存本地数据
        save_txt(mails[gid], f'groups/{gid}')
        count -= 1
        logT(f'群号:{gid} 已爬取完成并保存')
        if not count:
            break
        randSleep(5, 10)
    logT('获取QQ号完成')
    driver.quit()  # 关闭浏览器
    return mails


def crawlGroupIds():
    logT('开始获取所有群号')
    url = f'https://qun.qq.com/member.html'
    driver = _launchChromeDriver()
    if not driver:
        return False
    driver.get(url=url)
    time.sleep(12)  # 等待扫码登录成功
    group_ids = _parse_group(driver)
    save_txt(group_ids, 'groupsNumber')
    driver.quit()
    logT('获取群号完成')
    return group_ids


if __name__ == '__main__':
    # crawlQQNum(['', ''])
    pass
