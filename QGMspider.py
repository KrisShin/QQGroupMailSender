from selenium import webdriver
import time
import os
import re


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


def _scroll_foot(driver):
    '''
    下拉界面
    '''
    js = "var q=document.documentElement.scrollTop=100000"
    return driver.execute_script(js)


def crawlQQNum(driverPath):
    url = f'https://qun.qq.com/member.html'
    try:
        driver = webdriver.Chrome(executable_path=driverPath)  # 手动输入插件路径
    except:
        return 0
    driver.get(url=url)
    time.sleep(12)  # 等待扫码登录成功
    group_ids = _parse_group(driver)
    for i, gid in enumerate(group_ids):
        if i and (not i%3):
            try:
                driver.quit()
                time.sleep(5)
                driver = webdriver.Chrome(executable_path=driverPath)  # 手动输入插件路径
            except:
                return 0
        gurl = f'https://qun.qq.com/member.html#gid={gid}'
        try:
            driver.get(url=gurl)
            if i and (not i%3):
                time.sleep(12)
            driver.refresh()
        except Exception as e:
            print(e)
            return
        time.sleep(3)
        max_n = 0
        while max_n < len(driver.page_source):
            max_n = len(driver.page_source)
            _scroll_foot(driver)
            time.sleep(0.5)  # 每2.5秒下拉一次刷新名单，直至刷新不到新名单位置
        mails = _parseMails(driver)  # 保存本地数据
        time.sleep(10)
        if not os.path.exists('groups'):
            os.mkdir('groups')
        with open(f'groups/{gid}.txt', 'w') as fs:
            fs.write('\n'.join(mails))
    driver.quit()  # 关闭浏览器
    return


if __name__ == '__main__':
    path = 'D:\Projects\pycode\QQGroupMail\chromedriver.exe'
    crawlQQNum(path)
