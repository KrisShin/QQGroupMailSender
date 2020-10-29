import time
from math import ceil
import platform

from selenium import webdriver

from QGMConf import os, re, randint, sleep, DATAPATH, CONFIGS
from utils import saveGroup, logT, randSleep,  saveConfig

DRIVERPATH = r'.\chromedriver.exe' if platform.system(
) == 'Windows' else r'./chromedriver'


def _parseMails(driver):
    html = driver.page_source  # 获取源码
    reg = re.compile(r'<td>\s*?([1-9]\d{4,11})\s*?</td>')
    qqs = re.findall(reg, html)
    if not qqs:
        return qqs
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
    except Exception as err:
        logT(f'err: {err} 请确认驱动版本以及是否在本文件夹内', 'err')
        return False


def crawlQQNum(group_ids):
    logT('开始获取所有QQ号')
    driver = _launchChromeDriver()
    if not driver:
        return 0
    count = randint(3, 5)
    logT(f'本次将爬取{count}个群')
    CONFIGS['newCrawled'] = []
    for gid in group_ids:
        if gid in CONFIGS['crawledGids']:
            continue
        gurl = f'https://qun.qq.com/member.html#gid={gid}'
        CONFIGS['crawlingGid'] = gid
        saveConfig()
        driver.get(url=gurl)
        driver.refresh()
        randSleep(10, 12)  # wating to scan
        _scroll2foot(driver)
        mails = _parseMails(driver)  # 保存本地数据
        if not mails:
            driver.quit()
            return -2
        saveGroup(mails, gid)
        logT(f'群号:{gid} 已获取完成并保存')
        CONFIGS['crawlingGid'] = ''
        CONFIGS['newCrawled'].append(gid)
        CONFIGS['crawledGids'].append(gid)
        saveConfig()
        count -= 1
        if not count:
            break
        randSleep(5, 10)
    else:
        driver.quit()
        return -1
    driver.quit()  # 关闭浏览器
    return 1


def crawlGroupIds():
    logT('开始获取所有群号')
    url = f'https://qun.qq.com/member.html'
    driver = _launchChromeDriver()
    if not driver:
        return 0
    driver.get(url=url)
    time.sleep(12)  # 等待扫码登录成功
    group_ids = _parse_group(driver)
    driver.quit()
    if not group_ids:
        return -2
    CONFIGS['gids'] = group_ids
    logT('获取群号完成')
    return 1


if __name__ == '__main__':
    # crawlQQNum(['', ''])
    pass
