# -*- coding:utf-8 -*-

# ==================BatchMailSender V1.3 ===========================

import tkinter
from tkinter import Entry, Label, Button, filedialog, StringVar
from tkinter.scrolledtext import ScrolledText
import tkinter.messagebox
from tkinter import END
# import time
import os
from QQMailSender import send
from QGMspider import crawlQQNum


class MyGUI():
    """@brief:使用GUI界面来选择邮箱附件所在的文件夹和邮箱通讯录
    """

    # 构造函数
    def __init__(self, window):
        self.mainWindow = window
        self.groupNum = ''
        self.driverPath = ''
        self.mymail = ''
        self.mailAuth = ''
        self.subject = ''
        self.mailFile = None
        self.mailImage = None
        self.mailContent = ''
        self.mails = []
        self.filePath = ''

    # 初始化窗口
    def set_init_window(self):
        self.mainWindow.title("QQ邮箱获取群发工具")  # 设置标题
        self.mainWindow.geometry('620x500+100+50')  # 设置尺寸
        self.mainWindow.attributes('-alpha', 1)  # 属性？

        # 提示标签
        Label(self.mainWindow,
              text="请提前安装chrome浏览器并下载对应版本的chromedriver\n驱动下载地址在本程序左下角",
              pady=5,
              justify='left').grid(column=0, row=0, columnspan=3)
        a = StringVar()
        Entry(self.mainWindow, textvariable=a, width=40,
              state='readonly').grid(row=99,
                                     column=0,
                                     columnspan=3,
                                     sticky='w')
        a.set('https://npm.taobao.org/mirrors/chromedriver/')

        Label(self.mainWindow, text="请输入群号:", padx=10).grid(column=0,
                                                            row=1,
                                                            sticky='e')
        self.GRPNUM = Entry(self.mainWindow)
        self.GRPNUM.grid(column=1, row=1, sticky='we')
        Label(self.mainWindow, text="请选择驱动:", padx=10).grid(column=0,
                                                            row=2,
                                                            sticky='e')
        self.DRVPATH = Label(self.mainWindow, text='')
        self.DRVPATH.grid(column=1, row=2, sticky='w')
        Button(self.mainWindow, text='点击选择',
               command=self._getDriverPath).grid(column=2, row=2)
        self.GETMAILSBTN = Button(self.mainWindow,
                                  text='获取群成员QQ邮箱',
                                  state='disabled',
                                  command=self._getMails)
        self.GETMAILSBTN.grid(column=0, row=3, columnspan=3)
        self.TIP1 = Label(self.mainWindow, text="")
        self.TIP1.grid(column=0, row=4, columnspan=3)

        Label(self.mainWindow, text="请输入你的邮箱:", padx=10).grid(column=0,
                                                              row=5,
                                                              sticky='e')
        self.MYMAIL = Entry(self.mainWindow, state='disabled')
        self.MYMAIL.grid(column=1, row=5, sticky='we')

        Label(self.mainWindow, text="请输入邮箱授权码:", padx=10).grid(column=0,
                                                               row=6,
                                                               sticky='e')
        self.MAILAUTHCODE = Entry(self.mainWindow, state='disabled')
        self.MAILAUTHCODE.grid(column=1, row=6, sticky='we')

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
        self.MAILIMGS = Label(self.mainWindow, text='')
        self.MAILIMGS.grid(column=1, row=9)
        self.MAILIMGBTN = Button(self.mainWindow,
                                 text='点击选择',
                                 state='disabled',
                                 command=self._getMailImg)
        self.MAILIMGBTN.grid(column=2, row=9)

        Label(self.mainWindow, text="选择邮件附件:", padx=10).grid(column=0,
                                                             row=10,
                                                             sticky='e')
        self.FILEPATH = Label(self.mainWindow, text='')
        self.FILEPATH.grid(column=1, row=10)
        self.MAILFILEBTN = Button(self.mainWindow,
                                  text='点击选择',
                                  state='disabled',
                                  command=self._getMailFile)
        self.MAILFILEBTN.grid(column=2, row=10)

        self.SENDBTN = Button(self.mainWindow,
                              text='群发邮件',
                              state='disabled',
                              command=self._sendMails)
        self.SENDBTN.grid(column=1, row=11)
        self.SAVEBTN = Button(self.mainWindow,
                              text='保存邮箱文件',
                              state='disabled',
                              command=self._saveMails)
        self.SAVEBTN.grid(column=2, row=11)
        self.TIP2 = Label(self.mainWindow, text="")
        self.TIP2.grid(column=0, row=12, columnspan=3)

    def _getMails(self):
        if self.groupNum and self.driverPath:
            mails = crawlQQNum(self.groupNum, self.driverPath)
            if mails:
                self.mails = mails
                self.TIP1.configure(text='获取邮箱成功')
                self.SAVEBTN.configure(state='normal')
                self.SENDBTN.configure(state='normal')
                self.MAILCON.configure(state='normal')
                # self.MAILFILEBTN.configure(state='normal')
                # self.MAILIMGS.configure(state='normal')
                self.MYMAIL.configure(state='normal')
                self.MAILAUTHCODE.configure(state='normal')
                self.MAILSUBJ.configure(state='normal')
            else:
                self.TIP1.configure(text='获取邮箱失败, 请检查是否成功授权或浏览器和驱动版本是否匹配')

    def _getDriverPath(self):
        groupNum = self.GRPNUM.get()
        if not groupNum:
            self.TIP1.configure(text='请先输入群号')
            return
        self.groupNum = self.GRPNUM.get()
        driverPath = filedialog.askopenfilename()
        if driverPath.endswith('chromedriver.exe'):
            self.TIP1.configure(text='')
            self.driverPath = driverPath
            self.DRVPATH.configure(text=self.driverPath)
            self.GETMAILSBTN.configure(state='normal')
        else:
            self.TIP1.configure(text='驱动文件选择错误, 请重新选择')
            self.GETMAILSBTN.configure(state='disabled')

    def _getMailFile(self):
        self.filePath = filedialog.askopenfilename()
        self.mailFile.configure(text=self.filePath)

    def _getMailImg(self):
        img = filedialog.askopenfilename()
        if img:
            self.mailImages = img
            self.mailFile.configure(text=self.filePath)

    # # 开始发送邮件

    def _sendMails(self):
        # self.test_mock()
        # attach_path = self.attach_dir['text']
        # bookFile = self.book_dir['text']
        email = self.MYMAIL.get()
        auth = self.MAILAUTHCODE.get()
        subject = self.MAILSUBJ.get()
        content = self.MAILCON.get(0.0, END)
        if email and auth and subject and content:
            msg = send(email, auth, subject, self.mails, content)
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
        self.mymail = '767710688@qq.com'
        self.mailAuth = 'ojosjwekknupbbha'
        # self.mails = ['2855829886@qq.com']


def gui_start():
    init_window = tkinter.Tk()
    main_gui = MyGUI(init_window)
    main_gui.set_init_window()
    main_gui.test_mock()
    init_window.mainloop()


if __name__ == '__main__':
    gui_start()
