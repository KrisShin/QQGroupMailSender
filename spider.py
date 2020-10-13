import time
import os
import re
import platform

from selenium import webdriver

from utils import save_txt, logT, randSleep, randint, sleep


DRIVERPATH = r'.\chromedriver.exe' if platform.system(
) == 'Windows' else r'./chromedriver'


def _parseMails(driver):
    html = driver.page_source  # 获取源码
    reg = re.compile(r'<td>\s*?([1-9]\d{4,11})\s*?</td>')
    qqs = re.findall(reg, html)
    mails = [f'{q}@qq.com' for q in qqs]
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
        randSleep(0.5, 2)
    return 1


def crawlQQNum(group_ids):
    count = randint(3, 5)
    mails = {}
    for gid in group_ids:
        if gid in os.listdir('groups'):
            continue
        try:
            driver = webdriver.Chrome(executable_path=DRIVERPATH)  # 手动输入插件路径
        except:
            return 0
        gurl = f'https://qun.qq.com/member.html#gid={gid}'
        driver.get(url=gurl)
        driver.refresh()
        sleep(12)  # wating to scan

        _scroll2foot(driver)
        mails[gid] = _parseMails(driver)  # 保存本地数据
        if not os.path.exists('groups'):
            os.mkdir('groups')
        save_txt(mails[gid], f'groups/{gid}')
        count -= 1
        logT(f'群号:{gid} 已爬取完成并保存')
        if not count:
            break
    driver.quit()  # 关闭浏览器
    return


def crawlGroupIds():
    logT('开始获取所有群号')
    url = f'https://qun.qq.com/member.html'
    try:
        driver = webdriver.Chrome(executable_path=DRIVERPATH)  # 手动输入插件路径
    except:
        logT('请确认驱动版本以及是否在本文件夹内', 'err')
        return 0
    driver.get(url=url)
    time.sleep(12)  # 等待扫码登录成功
    group_ids = _parse_group(driver)
    save_txt(group_ids, 'groupsNumber.txt')
    driver.quit()
    
    return group_ids


if __name__ == '__main__':
    crawlQQNum(['', ''])
