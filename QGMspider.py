from selenium import webdriver
import time
import os
import re


def _parseMails(driver):
    html = driver.page_source  # 获取源码
    driver.quit()  # 关闭浏览器
    reg = re.compile(r'<td>\s*?([1-9]\d{4,11})\s*?</td>')
    res = re.findall(reg, html)
    mails = []
    for qqnum in res:
        mails.append(f'{qqnum}@qq.com')
    return mails


def _scroll_foot(driver):
    '''
    下拉界面
    '''
    js = "var q=document.documentElement.scrollTop=100000"
    return driver.execute_script(js)


def crawlQQNum(group_id, driverPath):
    url = f'https://qun.qq.com/member.html#gid={group_id}'
    try:
        driver = webdriver.Chrome(executable_path=driverPath)  # 手动输入插件路径
    except:
        return 0
    driver.get(url=url)
    time.sleep(10)  # 等待扫码登录成功
    max_n = 0
    while max_n < len(driver.page_source):
        max_n = len(driver.page_source)
        _scroll_foot(driver)
        time.sleep(1)  # 每2.5秒下拉一次刷新名单，直至刷新不到新名单位置

    mails = _parseMails(driver)  # 保存本地数据
    return mails


if __name__ == '__main__':
    gid = '55523468'
    path = 'D:\projs\qqGroupMember\chromedriver.exe'
    crawlQQNum(gid, path)
