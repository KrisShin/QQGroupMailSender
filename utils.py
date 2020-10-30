from QGMConf import GROUPPATH, CONFPATH, json, CONFIGS, os, messagebox, TUTORIAL, sleep, logger, random, shutil


def cleanCache():
    '''清空groups文件夹并初始化CONFIGS'''
    shutil.rmtree(GROUPPATH, ignore_errors=True)
    os.makedirs(GROUPPATH)
    CONFIGS.update({
        'gids': [],
        'new': False,
        'crawlingGid': '',
        'newCrawled': [],
        'crawledGids': [],
        'sendingGid': '',
        'sendGids': []
    })
    saveConfig()


def saveConfig():
    '''保存配置文件'''
    with open(CONFPATH, 'w') as fc:
        fc.write(json.dumps(CONFIGS))


def saveGroup(data, filename, mode='w'):
    '''保存爬取的群号'''
    path = os.path.join(GROUPPATH, filename)
    if not os.path.exists(GROUPPATH):
        os.makedirs(GROUPPATH, 777)
    if not isinstance(data, str):
        data = json.dumps(data)
    with open(path, mode) as fs:
        fs.write(data)
    return True


def dialogMsg(msg='', m='info'):
    '''弹窗提示'''
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
