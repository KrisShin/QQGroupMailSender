from selenium import webdriver
import time
import os
import re
from utils import save_txt, logger


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
    save_txt('\n'.join(group_ids), 'groupIds.txt')
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
        logger.error([1, 2, 3], {'a': 123, 'v': 'c'}, 'hahah')
        return 0
    driver.get(url=url)
    time.sleep(12)  # 等待扫码登录成功
    group_ids = _parse_group(driver)
    for i, gid in enumerate(group_ids):
        try:
            driver.quit()
            driver = webdriver.Chrome(
                executable_path=driverPath)  # 手动输入插件路径
        except:
            return 0
        gurl = f'https://qun.qq.com/member.html#gid={gid}'
        try:
            driver.get(url=gurl)
            driver.refresh()
        except Exception as e:
            print(e)
            return
        max_n = 0
        while max_n < len(driver.page_source):
            max_n = len(driver.page_source)
            _scroll_foot(driver)
        mails = _parseMails(driver)  # 保存本地数据
        if not os.path.exists('groups'):
            os.mkdir('groups')
        with open(f'groups/{gid}.txt', 'w') as fs:
            fs.write('\n'.join(mails))
    driver.quit()  # 关闭浏览器
    return


if __name__ == '__main__':
    import platform
    path = '.\chromedriver.exe' if platform.system() == 'Windows' else './chromedriver'
    crawlQQNum(path)
