# -*- coding:utf-8 -*-

# ==================BatchMailSender V1.3 ===========================

import tkinter
from tkinter.constants import *
from tkinter import *
# from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
import tkinter.messagebox
from tkinter import END
import time
import os
import sender
from QGMspider import crawlQQNum


class MyGUI():
    """@brief:使用GUI界面来选择邮箱附件所在的文件夹和邮箱通讯录
    """

    # 构造函数
    def __init__(self, window):
        self.mainWindow = window
        self.groupNum = ''
        self.driverPath = ''
        self.mailContent = ''
        self.mails = []
        self.filePath = ''

    # 初始化窗口
    def set_init_window(self):
        self.mainWindow.title("QQMail Lite")  # 设置标题
        self.mainWindow.geometry('630x420+100+50')  # 设置尺寸
        self.mainWindow.attributes('-alpha', 1)  # 属性？

        # 设置标签
        Label(self.mainWindow, text="请提前安装chrome浏览器并下载对应版本的chromedriver\n下载地址:https://npm.taobao.org/mirrors/chromedriver/",
              pady=5).grid(column=0, row=0, columnspan=3)
        Label(self.mainWindow, text="请输入群号:", padx=10).grid(
            column=0, row=1, sticky='e')
        self.GRPNUM = Entry(self.mainWindow)
        self.GRPNUM.grid(column=1, row=1, sticky='we')
        Label(self.mainWindow, text="请选择驱动:", padx=10).grid(
            column=0, row=2, sticky='e')
        self.DRVPATH = Label(self.mainWindow, text='')
        self.DRVPATH.grid(column=1, row=2, sticky='w')
        Button(self.mainWindow, text='点击选择',
               command=self._getDriverPath).grid(column=2, row=2)
        self.GETMAILSBTN = Button(self.mainWindow, text='获取群成员QQ邮箱', state='disabled',
                                  command=self._getMails)
        self.GETMAILSBTN.grid(column=0, row=3, columnspan=3)
        self.TIP1 = Label(self.mainWindow, text="")
        self.TIP1.grid(column=0, row=4, columnspan=3)

        Label(self.mainWindow, text="请输入你的邮箱:", padx=10).grid(
            column=0, row=5, sticky='e')
        self.MYMAIL = Entry(self.mainWindow)
        self.MYMAIL.grid(column=1, row=5, sticky='we')
        Label(self.mainWindow, text="请输入邮箱授权码:", padx=10).grid(
            column=0, row=6, sticky='e')
        self.MAILAUTHCODE = Entry(self.mainWindow)
        self.MAILAUTHCODE.grid(column=1, row=6, sticky='we')

        Label(self.mainWindow, text="输入邮件内容:", padx=10).grid(
            column=0, row=7, sticky='e')
        self.MAILCON = ScrolledText(
            self.mainWindow, width=60, height=10, state='disabled')
        self.MAILCON.grid(column=1, row=7, columnspan=2)

        Label(self.mainWindow, text="选择邮件附件:", padx=10).grid(
            column=0, row=8, sticky='e')
        self.FILEPATH = Label(self.mainWindow, text='')
        self.FILEPATH.grid(column=1, row=8)
        self.MAILFILEBTN = Button(self.mainWindow, text='点击选择', state='disabled',
                                  command=self._getMailFile)
        self.MAILFILEBTN.grid(column=2, row=8)

        self.SENDBTN = Button(self.mainWindow, text='群发邮件', state='disabled',
                              command=self._sendMails)
        self.SENDBTN.grid(column=1, row=9)
        self.SAVEBTN = Button(self.mainWindow, text='保存邮箱文件', state='disabled',
                              command=self._saveMails)
        self.SAVEBTN .grid(column=2, row=9)
        self.TIP2 = Label(self.mainWindow, text="")
        self.TIP2.grid(column=0, row=10, columnspan=3)

        # self.MAILCON.insert(INSERT, "")
        # self.MAILCON.insert(END, "")

        # 设置确定/取消按钮
        # self.finish_button = Button(self.mainWindow, text="确定", bg='lightblue',
        #                             width=15, command=self.start_send_mail)  # 　command=self.test
        # self.finish_button.place(x=460, y=430, width=80, height=30)  #
        # self.cancel_button = Button(
        #     self.mainWindow, text="取消", bg='lightblue', width=15, command=self.mainWindow.quit)
        # self.cancel_button.place(x=370, y=430, width=80, height=30)  #

    # 选择附件目录

    def _getMails(self):
        if self.groupNum and self.driverPath:
            mails = crawlQQNum(self.groupNum, self.driverPath)
            if mails:
                self.mails = mails
                self.TIP1.configure(text='获取邮箱成功')
                self.SAVEBTN.configure(state='normal')
                self.SENDBTN.configure(state='normal')
                self.MAILCON.configure(state='normal')
                self.MAILFILEBTN.configure(state='normal')
            else:
                self.TIP1.configure(text='获取邮箱失败, 请检查浏览器和驱动版本是否匹配')

    def _getDriverPath(self):
        groupNum = self.GRPNUM.get()
        if not groupNum:
            self.TIP1.configure(text='请先输入群号')
            return
        self.groupNum = self.GRPNUM.get()
        driverPath = askopenfilename()
        if driverPath.endswith('chromedriver.exe'):
            self.TIP1.configure(text='')
            self.driverPath = driverPath
            self.DRVPATH.configure(text=self.driverPath)
            self.GETMAILSBTN.configure(state='normal')
        else:
            self.TIP1.configure(text='驱动文件选择错误, 请重新选择')
            self.GETMAILSBTN.configure(state='disabled')

    def _getMailFile(self):
        self.filePath = askopenfilename()
        self.MAILFILE.configure(text=self.filePath)

    # # 测试如何获取 ScrolledText 中的文本内容
    # def test(self):
    #     print(type(self.info_text.get(END)))    # str格式
    #     print(self.info_text.get(0.0, END))   # 获取ScrolledText中的文本内容-正文

    #     # print(self.attach_dir.get())   # 'Label' object has no attribute 'get'
    #     # print(self.book_dir.get())
    #     print(self.attach_dir['text'])    # 获取label中的文本内容-目录
    #     print(self.book_dir['text'])  # 获取label中的文本内容-通讯录
    #     self.init_window_name.quit

    # # 开始发送邮件--attach_path,bookFile,mail_content

    def _sendMails(self):

        # attach_path = self.attach_dir['text']
        # bookFile = self.book_dir['text']
        # mail_content = self.info_text.get(0.0,END)
        # BatchsMailSender.mailSend(attach_path,bookFile,mail_content)

        sender.mailSend(
            self.attach_dir['text'], self.book_dir['text'], self.info_text.get(0.0, END))

        self.mainWindow.quit

    def _saveMails(self):
        if not self.mails:
            self.TIP2.configure(text='请先获取邮箱')
            return
        f = open('./mails.txt', 'w')
        for mail in self.mails:
            f.write(f'{mail}\n')
        f.close()
        self.TIP2.configure(text='保存完成')
        os.startfile('./')


def gui_start():
    init_window = tkinter.Tk()
    main_gui = MyGUI(init_window)
    main_gui.set_init_window()
    init_window.mainloop()


if __name__ == '__main__':
    gui_start()
