# -*- coding:utf-8 -*-

import tkinter
from tkinter import Entry, Label, Button, filedialog, StringVar
from tkinter.scrolledtext import ScrolledText
from tkinter import END
import os
import datetime
from mailSender import sender
from spider import crawlQQNum, crawlGroupIds
from threading import Thread, Lock, enumerate as eu
from utils import logT, dialogMsg, json, DATAPATH
from collections import deque

N = 10  # 一次给10个人发送邮件

DEBUG = True


class MyGUI():
    """@brief:使用GUI界面来选择邮箱附件所在的文件夹和邮箱通讯录
    """

    # 构造函数
    def __init__(self, window):
        self.mainWindow = window
        self.gids = ''
        self.subject = ''
        self.mailFile = None
        self.mailImages = []
        self.mailContent = ''
        self.mails = {}
        self.threadLock = Lock()
        self.count = 0
        self.queue = deque()
        self.currentGroup = ''
        self.status = True

    # 初始化窗口
    def set_init_window(self):
        self.mainWindow.title("Pow Mail Tool")  # 设置标题
        self.mainWindow.geometry('620x330+100+50')  # 设置尺寸
        self.mainWindow.attributes('-alpha', 1)  # 属性？

        # 驱动下载地址
        Label(self.mainWindow, text="驱动下载地址: ").grid(
            column=0, row=0, sticky='e')
        a = StringVar()
        Entry(self.mainWindow, textvariable=a, width=50,
              state='readonly').grid(row=0, column=1, columnspan=2, sticky='w')
        a.set('https://npm.taobao.org/mirrors/chromedriver/')

        self.GETGIDSBTN = Button(self.mainWindow,
                                 text='获取群号',
                                 command=self.getGids)
        self.GETGIDSBTN.grid(column=0, row=1, sticky='e')

        self.READGIDSBTN = Button(self.mainWindow,
                                  text='读取群号',
                                  command=self.readGids)
        self.READGIDSBTN.grid(column=1, row=1)

        self.STARTCRAWLBTN = Button(self.mainWindow,
                                    text='读取邮箱',
                                    command=self.readMails)
        self.STARTCRAWLBTN.grid(column=2, row=1)

        self.STARTCRAWLBTN = Button(self.mainWindow,
                                    text='开始爬取',
                                    state='disabled',
                                    command=self.getMails)
        self.STARTCRAWLBTN.grid(column=3, row=1)

        Label(self.mainWindow, text="请输入邮件主题:", padx=10).grid(column=0,
                                                              row=2,
                                                              sticky='e')
        self.MAILSUBJ = Entry(self.mainWindow, state='disabled')
        self.MAILSUBJ.grid(column=1, row=2, sticky='we')

        Label(self.mainWindow, text="输入邮件内容:", padx=10).grid(column=0,
                                                             row=3,
                                                             sticky='e')
        self.MAILCON = ScrolledText(self.mainWindow,
                                    width=65,
                                    height=10,
                                    state='disabled')
        self.MAILCON.grid(column=1, row=3, columnspan=3)

        Label(self.mainWindow, text="选择邮件图片:", padx=10).grid(column=0,
                                                             row=4,
                                                             sticky='e')
        self.MAILIMG = Label(self.mainWindow, text='')
        self.MAILIMG.grid(column=1, row=4)
        self.MAILIMGBTN = Button(self.mainWindow,
                                 text='点击选择',
                                 state='disabled',
                                 command=self.getMailImg)
        self.MAILIMGBTN.grid(column=2, row=4)

        self.MAILCLEANIMGBTN = Button(self.mainWindow,
                                      text='清空图片',
                                      state='disabled',
                                      command=self._cleanMailImg)
        self.MAILCLEANIMGBTN.grid(column=3, row=4)

        Label(self.mainWindow, text="选择邮件附件:", padx=10).grid(column=0,
                                                             row=5,
                                                             sticky='e')
        self.FILEPATH = Label(self.mainWindow, text='')
        self.FILEPATH.grid(column=1, row=5)
        self.MAILFILEBTN = Button(self.mainWindow,
                                  text='点击选择',
                                  state='disabled',
                                  command=self.getMailFile)
        self.MAILFILEBTN.grid(column=2, row=5)

        self.SENDBTN = Button(self.mainWindow,
                              text='群发邮件',
                              state='disabled',
                              command=self.sendMails)
        self.SENDBTN.grid(column=1, row=6, columnspan=2)

        self.TIP = Label(text='')
        self.TIP.grid(column=0, row=7, columnspan=4)
        dialogMsg(m='t')
        logT('启动程序')

    def getGids(self):
        '''扫码获取所有群号'''
        gids = crawlGroupIds()
        if not gids:
            dialogMsg('请确认驱动版本以及是否在本文件夹内', 'err')
        else:
            logT(f'获取群号成功: {gids}')
            dialogMsg('获取群号成功')
            self.gids = gids
            self.STARTCRAWLBTN.configure(state='normal')

    def readGids(self):
        try:
            with open('groupsNumber', 'r') as gs:
                strs = gs.read()
                try:
                    gids = json.loads(strs)
                    if not gids:
                        logT('groupsNumber没有内容', 'err')
                        dialogMsg('groupsNumber没有内容', 'err')
                        return False
                    self.gids = gids
                except json.decoder.JSONDecodeError:
                    logT('groupsNumber内容解析失败', 'err')
                    dialogMsg('groupsNumber文件内容格式不是json', 'err')
                    return False
                dialogMsg('读取群号成功')
                logT(f'读取群号成功: {gids}')
                self.STARTCRAWLBTN.configure(state='normal')
                return True
        except FileNotFoundError:
            try:
                with open(os.path.join(DATAPATH, 'groupsNumber'), 'r') as gs:
                    strs = gs.read()
                    gids = json.loads(strs)
                    if not gids:
                        logT('groupsNumber没有内容', 'err')
                        dialogMsg('请重新获取群号', 'err')
                        return False
                    self.gids = gids
                    dialogMsg(f'读取群号成功{gids}')
                    logT('读取群号成功')
                    self.STARTCRAWLBTN.configure(state='normal')
            except FileNotFoundError:
                dialogMsg('没有找到groupsNumber文件', 'err')

    def readMails(self):
        try:
            gidFiles = os.listdir(os.path.join(DATAPATH, 'groups'))
            if gidFiles:
                mails = {}
                for gid in gidFiles:
                    with open(os.path.join(DATAPATH, f'groups/{gid}'), 'r') as fg:
                        mails[gid] = json.loads(fg.read())
                self.mails = mails
                self._setWidgetState('normal')
                dialogMsg('读取邮箱完成')
                logT(f'读取邮箱完成， 群号：{gidFiles}')
                return True
            msg = ('没有群邮箱文件在groups文件夹内', 'err')
            logT(*msg)
            dialogMsg(*msg)
        except FileNotFoundError:
            logT('没有groups文件夹', 'err')
            dialogMsg('请先获取邮箱', 'err')

    def getMails(self):
        res = crawlQQNum(self.gids)
        if res:
            self.mails = res
            self._setWidgetState('normal')
            dialogMsg('获取邮箱成功')
        else:
            msg = ('获取邮箱失败, 请检查是否成功授权或浏览器和驱动版本是否匹配', 'err')
            logT(*msg)
            dialogMsg(*msg)

    def _setWidgetState(self, mode):
        self.MAILSUBJ.configure(state=mode)
        self.MAILCON.configure(state=mode)
        self.MAILIMGBTN.configure(state=mode)
        self.MAILFILEBTN.configure(state=mode)
        self.SENDBTN.configure(state=mode)

    def getMailFile(self):
        f = filedialog.askopenfilename()
        if f:
            logT(f'添加附件成功 {f}')
            self.mailFile = f
            self.FILEPATH.configure(text=self.mailFile)

    def getMailImg(self):
        img = filedialog.askopenfilename()
        ext = os.path.splitext(img)[-1]
        if img and ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            logT(f'添加图片成功 {img}')
            self.mailImages.append(img)
            imgs = [os.path.split(img)[-1] for img in self.mailImages]
            self.MAILIMG.configure(text=','.join(imgs))
            self.MAILCLEANIMGBTN.configure(state='normal')

    def _cleanMailImg(self):
        self.mailImages = []
        self.MAILIMG.configure(text='')
        logT('清空图片')
        self.MAILCLEANIMGBTN.configure(state='disabled')

    def _readAccount(self):
        try:
            with open('account.json', 'r') as fa:
                acStr = fa.read()
                try:
                    data = json.loads(acStr)
                    return data
                except:
                    msg = ('解析账号失败, 请检查账号格式', 'err')
                    logT(*msg)
                    dialogMsg(*msg)
                    return False
        except FileNotFoundError:
            msg = ('获取发件账号失败, 当前目录下没有account.json', 'err')
            logT(*msg)
            dialogMsg(*msg)
            return False

    def _senderThread(self, email, auth, mailType, mail):
        def __loop():
            while self.queue and self.status:
                receivers = self.queue.popleft()
                num = sender(email, auth, mailType, receivers, mail)
                with self.threadLock:
                    if not self.status:
                        return False
                    if num == 0:
                        msg = (f"请检查{email}邮箱和授权码", 'err')
                        logT(*msg)
                        dialogMsg(*msg)
                        self.status = False
                        return False
                    self.count += num
                    logT(
                        f'total: {self.count} {email} send to mails: {receivers[0]} - {receivers[-1]}')
                    self.TIP.configure(text=f'邮件成功发送给{self.count}个人, 5秒后刷新')
        if self.queue and self.status:
            __loop()
        if self.currentGroup and self.status:
            with self.threadLock:
                logT(f'群{self.currentGroup} 已全部发送')
                groupFile = os.path.join(
                    DATAPATH, 'groups', self.currentGroup)
                if os.path.exists(groupFile):
                    os.remove(groupFile)
                    print(
                        f'remove {self.currentGroup} at {datetime.datetime.now()}')

        if self.status:
            for group in self.mails:
                self.queue.extend(self.mails[group])
                self.currentGroup = group
                del self.mails[group]
                break

    def _senderManager(self, accounts, mail):
        self._setWidgetState('disabled')
        tds = list()
        for mailType in accounts:
            for acc in accounts[mailType]:
                sendThread = Thread(target=self._senderThread,
                                    args=(acc['email'], acc['auth'], mailType, mail))
                tds.append(sendThread)
                sendThread.start()
        for td in tds:
            td.join()
        if self.status:
            msg = f'发送完成, 邮件成功发送给{self.count}个人'
            logT(msg)
            dialogMsg(msg)
            self.TIP.configure(text=msg)
            self._setWidgetState('normal')
            return
        msg = ("发送失败, 请检查账号或者稍后再试", 'err')
        self.TIP.configure(text=msg[0])
        logT(*msg)
        dialogMsg(*msg)
        return

    # 开始发送邮件

    def sendMails(self):
        self.status = True
        self.count = 0
        subject = self.MAILSUBJ.get()
        content = self.MAILCON.get(0.0, END)
        accounts = self._readAccount()
        if not accounts:
            return
        mail = {
            'subject': subject,
            'content': content,
            'images': self.mailImages,
            'attach': self.mailFile
        }
        if accounts and subject and content:
            self.TIP.configure(text='开始发送邮件, 请等待或者查看日志')
            td = Thread(target=self._senderManager, args=(accounts, mail))
            td.start()
        else:
            msg = ('请完整填写邮件主题和正文', 'err')
            logT(*msg)
            dialogMsg(*msg)

    def test_mock(self):
        self.mymail = '767710688@qq.com'
        self.mailAuth = 'ojosjwekknupbbha'
        self.mymail = '2855829886@qq.com'
        self.mailAuth = 'diplnzgchsmrdgbb'


def gui_start():
    init_window = tkinter.Tk()
    main_gui = MyGUI(init_window)
    main_gui.set_init_window()
    init_window.mainloop()


if __name__ == '__main__':
    gui_start()
