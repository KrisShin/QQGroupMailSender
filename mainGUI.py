# -*- coding:utf-8 -*-

import tkinter
from tkinter import Entry, Label, Button, filedialog, StringVar
from tkinter.scrolledtext import ScrolledText
from tkinter import END
import os
import json
from mailSender import sender
from spider import crawlQQNum, crawlGroupIds
from threading import Thread
from utils import logT, dialogMsg

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

    # 初始化窗口
    def set_init_window(self):
        self.mainWindow.title("Pow Mail Tool")  # 设置标题
        self.mainWindow.geometry('620x500+100+50')  # 设置尺寸
        self.mainWindow.attributes('-alpha', 1)  # 属性？

        # 驱动下载地址
        Label(self.mainWindow, text="下载地址: ").grid(
            column=0, row=0, sticky='e')
        a = StringVar()
        Entry(self.mainWindow, textvariable=a, width=40,
              state='readonly').grid(row=0, column=1, columnspan=2, sticky='w')
        a.set('https://npm.taobao.org/mirrors/chromedriver/')

        self.GETGIDSBTN = Button(self.mainWindow,
                                 text='获取群号',
                                 command=self._getGids)
        self.GETGIDSBTN.grid(column=0, row=1, sticky='e')

        self.READGIDSBTN = Button(self.mainWindow,
                                  text='读取群号',
                                  command=self._readGids)
        self.READGIDSBTN.grid(column=1, row=1)

        self.STARTCRAWLBTN = Button(self.mainWindow,
                                    text='开始爬取',
                                    state='disabled',
                                    command=self._getMails)
        self.STARTCRAWLBTN.grid(column=2, row=1, sticky='w')

        Label(self.mainWindow, text="请输入邮件主题:", padx=10).grid(column=0,
                                                              row=7,
                                                              sticky='e')
        self.MAILSUBJ = Entry(self.mainWindow, state='disabled')
        self.MAILSUBJ.grid(column=1, row=7, sticky='we')

        Label(self.mainWindow, text="输入邮件内容:", padx=10).grid(column=0,
                                                             row=8,
                                                             sticky='e')
        self.MAILCON = ScrolledText(self.mainWindow,
                                    width=60,
                                    height=10,
                                    state='disabled')
        self.MAILCON.grid(column=1, row=8, columnspan=2)

        Label(self.mainWindow, text="选择邮件图片:", padx=10).grid(column=0,
                                                             row=9,
                                                             sticky='e')
        self.MAILIMG = Label(self.mainWindow, text='')
        self.MAILIMG.grid(column=1, row=9)
        self.MAILIMGBTN = Button(self.mainWindow,
                                 text='点击选择',
                                 #  state='disabled',
                                 command=self._getMailImg)
        self.MAILIMGBTN.grid(column=2, sticky='w', row=9)

        self.MAILCLEANIMGBTN = Button(self.mainWindow,
                                      text='清空图片',
                                      #  state='disabled',
                                      command=self._cleanMailImg)
        self.MAILCLEANIMGBTN.grid(column=2, sticky='e', row=9)

        Label(self.mainWindow, text="选择邮件附件:", padx=10).grid(column=0,
                                                             row=10,
                                                             sticky='e')
        self.FILEPATH = Label(self.mainWindow, text='')
        self.FILEPATH.grid(column=1, row=10)
        self.MAILFILEBTN = Button(self.mainWindow,
                                  text='点击选择',
                                  state='disabled',
                                  command=self._getMailFile)
        self.MAILFILEBTN.grid(column=2, row=10, sticky='w')

        self.SENDBTN = Button(self.mainWindow,
                              text='群发邮件',
                              state='disabled',
                              command=self._sendMails)
        self.SENDBTN.grid(column=1, row=11)
        self.TIP2 = Label(self.mainWindow, text="")
        self.TIP2.grid(column=0, row=12, columnspan=3)

        dialogMsg(m='t')

    def _getGids(self):
        '''扫码获取所有群号'''
        gids = crawlGroupIds()
        if gids == 0:
            dialogMsg('请确认驱动版本以及是否在本文件夹内', 'err')
        else:
            dialogMsg('获取群号成功')
            self.STARTCRAWLBTN.configure(state='normal')

    def _readGids(self):
        try:
            with open('groupsNumber.txt', 'r') as gs:
                strs = gs.read()
                try:
                    gids = json.loads(strs)
                    self.gids = gids
                    dialogMsg('读取群号成功')
                    self.STARTCRAWLBTN.configure(state='normal')
                except json.decoder.JSONDecodeError:
                    dialogMsg('groupsNumber.txt文件内容格式不是json\n请点击获取群号')
        except FileNotFoundError:
            dialogMsg('当前文件夹没有groupsNumber.txt文件')

    def _getMails(self):
        mails = crawlQQNum(self.gids)
        if mails:
            self.mails = mails
            self.SENDBTN.configure(state='normal')
            self.MAILCON.configure(state='normal')
            self.MAILIMGBTN.configure(state='normal')
            self.MAILFILEBTN.configure(state='normal')
            self.MAILSUBJ.configure(state='normal')
        else:
            logT('获取邮箱失败, 请检查是否成功授权或浏览器和驱动版本是否匹配', 'err')
            dialogMsg('获取邮箱失败\n请检查是否成功授权或浏览器和驱动版本是否匹配', 'err')

    def _getMailFile(self):
        f = filedialog.askopenfilename()
        if f:
            self.mailFile = f
            self.FILEPATH.configure(text=self.mailFile)

    def _getMailImg(self):
        img = filedialog.askopenfilename()
        ext = os.path.splitext(img)[-1]
        if img and ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            self.mailImages.append(img)
            imgs = [os.path.split(img)[-1] for img in self.mailImages]
            self.MAILIMG.configure(text=','.join(imgs))

    def _cleanMailImg(self):
        self.mailImages = []
        self.MAILIMG.configure(text='')

    def _threadSender(self, email, auth, subject, content, imgPath, filePath):
        users = self.mails[:N]
        num = 0
        while users:
            num += sender(email, auth, subject, users, content, self.TIP2, num,
                          imgPath, filePath)
            users = self.mails[num:num + N]
            if not num:
                msg = "发送失败, 请换QQ或者稍后再试"
                self.TIP2.configure(text=msg)
                return
        self.TIP2.configure(text=f"发送完成, 邮件成功发送给{num}个人")

    # # 开始发送邮件

    def _sendMails(self):
        # self.test_mock()
        # attach_path = self.attach_dir['text']
        # bookFile = self.book_dir['text']
        # if DEBUG:
        #     sendThread = Thread(
        #         target=self._threadSender,
        #         args=(self.mymail, self.mailAuth, 'hello world',
        #               'hello content',
        #               r'D:\Projects\pycode\QQGroupMail\test.png',
        #               r'D:\Projects\pycode\QQGroupMail\mails.txt'))
        #     sendThread.start()
        #     return
        email = self.MYMAIL.get()
        auth = self.MAILAUTHCODE.get()
        subject = self.MAILSUBJ.get()
        content = self.MAILCON.get(0.0, END)
        if email and auth and subject and content:
            sendThread = Thread(target=self._threadSender,
                                args=(email, auth, subject, content,
                                      self.mailImages, self.mailFile))
            sendThread.start()
        else:
            msg = '请完整填写邮箱, 授权码, 邮件主题和正文'
        self.TIP2.configure(text=msg)

    def _saveMails(self):
        if not self.mails:
            self.TIP2.configure(text='请先获取邮箱')
            return
        f = open('./mails.txt', 'w')
        for mail in self.mails:
            f.write(f'{mail}\n')
        f.close()
        self.TIP2.configure(text='保存完成')
        os.startfile(os.path.abspath('.'))

    def test_mock(self):
        # self.mymail = '767710688@qq.com'
        # self.mailAuth = 'ojosjwekknupbbha'
        # self.mails = ['2855829886@qq.com']

        self.mymail = '2855829886@qq.com'
        self.mailAuth = 'diplnzgchsmrdgbb'
        self.mails = ['767710688@qq.com']


def gui_start():
    init_window = tkinter.Tk()
    main_gui = MyGUI(init_window)
    main_gui.set_init_window()
    init_window.mainloop()


if __name__ == '__main__':
    gui_start()
