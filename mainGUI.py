# -*- coding:utf-8 -*-

import tkinter
from tkinter import Entry, Label, Button, filedialog, StringVar
from tkinter.scrolledtext import ScrolledText
from tkinter import END
import os
from mailSender import sender
from spider import crawlQQNum, crawlGroupIds
from threading import Thread, Lock
from utils import logT, dialogMsg, json

N = 10  # 一次给10个人发送邮件

DEBUG = True


class MyGUI():
    """@brief:使用GUI界面来选择邮箱附件所在的文件夹和邮箱通讯录
    """

    # 构造函数
    def __init__(self, window):
        self.mainWindow = window
        self.gids = ''
        self.mymail = ''
        self.mailAuth = ''
        self.subject = ''
        self.mailFile = None
        self.mailImages = []
        self.mailContent = ''
        self.mails = []
        self.countLock = Lock()
        self.count = 0

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
        # dialogMsg(m='t')
        logT('启动程序')

    def getGids(self):
        '''扫码获取所有群号'''
        gids = crawlGroupIds()
        if not gids:
            dialogMsg('请确认驱动版本以及是否在本文件夹内', 'err')
        else:
            dialogMsg('获取群号成功')
            self.STARTCRAWLBTN.configure(state='normal')

    def readGids(self):
        try:
            with open('groupsNumber.txt', 'r') as gs:
                strs = gs.read()
                try:
                    gids = json.loads(strs)
                    self.gids = gids
                    dialogMsg('读取群号成功')
                    self.STARTCRAWLBTN.configure(state='normal')
                except json.decoder.JSONDecodeError:
                    dialogMsg('groupsNumber.txt文件内容格式不是json\n请点击获取群号', 'err')
        except FileNotFoundError:
            dialogMsg('当前文件夹没有groupsNumber.txt文件', 'err')

    def readMails(self):
        try:
            gidFiles = os.listdir('groups')
            mails = {}
            if gidFiles:
                for gid in gidFiles:
                    with open(f'groups/{gid}', 'r') as fg:
                        mails[gid] = json.loads(fg.read())
                self._setMails(mails)
                dialogMsg('读取邮箱完成')
                logT(f'读取邮箱完成， 群号：{gidFiles}')
                return
            msg = ('没有群邮箱文件在groups文件夹内', 'err')
            logT(msg)
            dialogMsg(msg)
        except FileNotFoundError:
            msg = ('没有groups文件夹', 'err')
            logT(msg)
            dialogMsg(msg)

    def getMails(self):
        res = crawlQQNum(self.gids)
        if res:
            self._setMails(res)
        else:
            msg = ('获取邮箱失败, 请检查是否成功授权或浏览器和驱动版本是否匹配', 'err')
            logT(*msg)
            dialogMsg(*msg)

    def _setMails(self, mails):
        self.mails = mails
        self.MAILSUBJ.configure(state='normal')
        self.MAILCON.configure(state='normal')
        self.MAILIMGBTN.configure(state='normal')
        self.MAILFILEBTN.configure(state='normal')
        self.SENDBTN.configure(state='normal')

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

    def _cleanMailImg(self):
        self.mailImages = []
        self.MAILIMG.configure(text='')
        logT('清空图片')

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

    def _threadSender(self, email, auth, mailType, mail):
        for group in self.mails:
            receivers = self.mails[group][:N]
            while receivers:
                num = sender(email, auth, mailType, receivers, mail)
                if num == 0:
                    msg = ("发送失败, 请检查账号或者稍后再试", 'err')
                    logT(*msg)
                    dialogMsg(*msg)
                    return
                with self.countLock:
                    self.count += num
                self.TIP.configure(text=f'邮件成功发送给{self.count}个人, 5秒后刷新')
                receivers = self.mails[group][self.count:self.count + N]
        msg = f"发送完成, 邮件成功发送给{self.count}个人"
        logT(msg)
        dialogMsg(msg)

    # 开始发送邮件

    def sendMails(self):
        self.count = 0
        subject = self.MAILSUBJ.get()
        content = self.MAILCON.get(0.0, END)
        accounts = self._readAccount()
        mail = {
            'subject': subject,
            'content': content,
            'images': self.mailImages,
            'attach': self.mailFile
        }
        if accounts and subject and content:
            self.TIP.configure(text='开始发送邮件, 请等待或者查看日志')
            for mailType in accounts:
                for acc in accounts[mailType]:
                    sendThread = Thread(target=self._threadSender,
                                        args=(acc['email'], acc['auth'], mailType, mail))
                    sendThread.start()
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
