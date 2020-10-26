# -*- coding:utf-8 -*-

from collections import deque
import datetime
import os
from tkinter import Entry, Label, Button, filedialog, StringVar, Scrollbar, Listbox, Tk, ttk
from tkinter.scrolledtext import ScrolledText

from mailSender import sender
from spider import crawlQQNum, crawlGroupIds
from threading import Thread, Lock, enumerate as eu
from utils import logT, dialogMsg, json, DATAPATH

N = 10  # 一次给10个人发送邮件
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 430


class MyGUI():
    """@brief:使用GUI界面来选择邮箱附件所在的文件夹和邮箱通讯录
    """

    # 构造函数
    def __init__(self, window):
        self.mainWindow = window
        self.gids = []
        self.subject = ''
        self.mail = {'subject': '', 'content': '',
                     'images': [], 'attach': None}
        self.mails = {}
        self.threadLock = Lock()
        self.count = 0
        self.total = 0
        self.queue = deque()
        self.status = True

    # 初始化窗口
    def set_init_window(self):
        self.mainWindow.title("Pow Mail Tool")  # 设置标题
        self.mainWindow.geometry(
            f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+100+50')  # 设置尺寸
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

        self.STARTCRAWLBTN = Button(self.mainWindow,
                                    text='读取邮箱',
                                    command=self.readMails)
        self.STARTCRAWLBTN.grid(column=1, row=1, columnspan=2)

        self.STARTCRAWLBTN = Button(self.mainWindow,
                                    text='开始爬取',
                                    state='disabled',
                                    command=self.getMails)
        self.STARTCRAWLBTN.grid(column=3, row=1)

        Label(self.mainWindow, text="选择要发送邮件的群\n(右侧双击删除)",
              padx=10).grid(column=0, row=2, sticky='e')
        self.ALLGROUPLIST = Listbox(
            self.mainWindow, height=5, selectmode='multiple', state='disabled')
        self.ALLGROUPLIST.grid(column=1, row=2)
        self.CHOOSEGROUPBTN = Button(
            self.mainWindow, text='>>', state='disabled', width=10, command=self.chooseGroup)
        self.CHOOSEGROUPBTN.grid(column=2, row=2)
        self.CHOOSEGROUPLIST = Listbox(
            self.mainWindow, height=5, state='disabled')
        self.CHOOSEGROUPLIST.grid(column=3, row=2)
        self.CHOOSEGROUPLIST.bind(
            '<Double-Button-1>', self.deleteGroup)  # 双击删除gid

        Label(self.mainWindow, text="请输入邮件主题:", padx=10).grid(column=0,
                                                              row=3,
                                                              sticky='e')
        self.MAILSUBJ = Entry(self.mainWindow, state='disabled')
        self.MAILSUBJ.grid(column=1, row=3, sticky='we')

        Label(self.mainWindow, text="输入邮件内容:", padx=10).grid(column=0,
                                                             row=4,
                                                             sticky='e')
        self.MAILCON = ScrolledText(self.mainWindow,
                                    width=65,
                                    height=10,
                                    state='disabled')
        self.MAILCON.grid(column=1, row=4, columnspan=3)

        Label(self.mainWindow, text="选择邮件图片:", padx=10).grid(column=0,
                                                             row=5,
                                                             sticky='e')
        self.MAILIMG = Label(self.mainWindow, text='')
        self.MAILIMG.grid(column=1, row=5)
        self.MAILIMGBTN = Button(self.mainWindow,
                                 text='点击选择',
                                 state='disabled',
                                 command=self.getMailImg)
        self.MAILIMGBTN.grid(column=2, row=5)

        self.MAILCLEANIMGBTN = Button(self.mainWindow,
                                      text='清空图片',
                                      state='disabled',
                                      command=self._cleanMailImg)
        self.MAILCLEANIMGBTN.grid(column=3, row=5)

        Label(self.mainWindow, text="选择邮件附件:", padx=10).grid(column=0,
                                                             row=6,
                                                             sticky='e')
        self.FILEPATH = Label(self.mainWindow, text='')
        self.FILEPATH.grid(column=1, row=6)
        self.MAILFILEBTN = Button(self.mainWindow,
                                  text='点击选择',
                                  state='disabled',
                                  command=self.getMailFile)
        self.MAILFILEBTN.grid(column=2, row=6)

        self.SENDBTN = Button(self.mainWindow,
                              text='群发邮件',
                              state='disabled',
                              command=self.sendMails)
        self.SENDBTN.grid(column=0, row=7)

        self.PROGERSS = ttk.Progressbar(
            self.mainWindow, orient="horizontal", length=300, mode="determinate")
        self.PROGERSS.grid(column=1, row=7, columnspan=3)

        self.TIP = Label(text='')
        self.TIP.grid(column=0, row=8, columnspan=4)

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

    def readMails(self):
        try:
            gidFiles = os.listdir(os.path.join(DATAPATH, 'groups'))
            if gidFiles:
                mails = {}
                total = 0
                for gid in gidFiles:
                    with open(os.path.join(DATAPATH, f'groups/{gid}'), 'r') as fg:
                        mails[gid] = json.loads(fg.read())
                        total += (len(mails[gid])-1) * \
                            10 + len(mails[gid][-1])
                self.mails = mails
                self._setWidgetState('normal')
                self.ALLGROUPLIST.insert('end', *mails.keys())
                dialogMsg(f'读取邮箱完成, 共{total}人')
                logT(f'读取邮箱完成, 共{total}人，群号：{gidFiles}')
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
            self.ALLGROUPLIST.insert('end', res.keys())
            dialogMsg('获取邮箱成功')
        else:
            msg = ('获取邮箱失败, 请检查是否成功授权或浏览器和驱动版本是否匹配', 'err')
            logT(*msg)
            dialogMsg(*msg)

    def chooseGroup(self):
        idxs = self.ALLGROUPLIST.curselection()
        for idx in idxs:
            gid = self.ALLGROUPLIST.get(idx)
            if gid not in self.gids:
                self.gids.append(gid)
                self.CHOOSEGROUPLIST.insert('end', gid)

    def deleteGroup(self, idx):
        gid = self.CHOOSEGROUPLIST.get('active')
        self.CHOOSEGROUPLIST.delete(0, 'end')
        self.gids.remove(gid)
        self.CHOOSEGROUPLIST.insert('end', *self.gids)

    def _setWidgetState(self, mode):
        self.ALLGROUPLIST.configure(state=mode)
        self.CHOOSEGROUPBTN.configure(state=mode)
        self.CHOOSEGROUPLIST.configure(state=mode)
        self.MAILSUBJ.configure(state=mode)
        self.MAILCON.configure(state=mode)
        self.MAILIMGBTN.configure(state=mode)
        self.MAILFILEBTN.configure(state=mode)
        self.SENDBTN.configure(state=mode)

    def getMailFile(self):
        f = filedialog.askopenfilename()
        if f:
            logT(f'添加附件成功 {f}')
            self.mail['attach'] = f
            filename = os.path.split(f)[-1]
            self.FILEPATH.configure(text=filename)

    def getMailImg(self):
        img = filedialog.askopenfilename()
        ext = os.path.splitext(img)[-1]
        if img and ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            logT(f'添加图片成功 {img}')
            self.mail['images'].append(img)
            imgs = [os.path.split(img)[-1] for img in self.mail['images']]
            self.MAILIMG.configure(text=','.join(imgs))
            self.MAILCLEANIMGBTN.configure(state='normal')

    def _cleanMailImg(self):
        self.mail['images'] = []
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
        while self.queue and self.status:
            receivers = self.queue.popleft()
            num = sender(email, auth, mailType, receivers, mail)
            with self.threadLock:
                if not self.status:
                    return False
                if num != len(receivers):
                    msg = (f"请检查{email}邮箱和授权码", 'err')
                    logT(*msg)
                    dialogMsg(*msg)
                    self.status = False
                    return False
                self.count += num
                logT(f'sent: {self.count} {email} send to mails: {receivers}')
                self.TIP.configure(
                    text=f'邮件成功发送给{self.count}个人, 共{self.total}人, 请等待刷新')
                self.PROGERSS['value'] = (self.count/self.total)*100

    def _senderManager(self, accounts, mail):
        self._setWidgetState('disabled')
        tds = list()
        for gid in self.mails:
            if gid not in self.gids:
                continue
            self.queue.extend(self.mails[gid])
            logT(f'开始向群: {gid} 的成员发送邮件')
            for mailType in accounts:
                for acc in accounts[mailType]:
                    sendThread = Thread(target=self._senderThread,
                                        args=(acc['email'], acc['auth'], mailType, mail))
                    tds.append(sendThread)
                    sendThread.start()
            for td in tds:
                td.join()
            if not self.status:
                break
            logT(f'群{gid} 已全部发送')
            self.CHOOSEGROUPLIST.delete(0, 'end')
            self.gids.remove(gid)
            self.CHOOSEGROUPLIST.insert('end', *self.gids)
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
        self.mail['subject'] = self.MAILSUBJ.get()
        self.mail['content'] = self.MAILCON.get(0.0, 'end')
        accounts = self._readAccount()
        if not accounts:
            return
        if accounts and self.mail['subject'] and self.mail['content'] and self.gids:
            self.TIP.configure(text='开始发送邮件, 请等待或者查看日志')
            self.total = 0
            for gid in self.gids:
                self.total += (len(self.mails[gid])-1) * \
                    10 + len(self.mails[gid][-1])
            logT(f'开始发送邮件, 选择群号: {self.gids}, 共{self.total}人')
            td = Thread(target=self._senderManager, args=(accounts, self.mail))
            td.start()
        else:
            msg = ('请选择要发送的群号并完整填写邮件主题和正文', 'err')
            logT(*msg)
            dialogMsg(*msg)

    def test_mock(self):
        self.mymail = '767710688@qq.com'
        self.mailAuth = 'ojosjwekknupbbha'
        self.mymail = '2855829886@qq.com'
        self.mailAuth = 'diplnzgchsmrdgbb'


def gui_start():
    init_window = Tk()
    main_gui = MyGUI(init_window)
    main_gui.set_init_window()
    init_window.mainloop()


if __name__ == '__main__':
    gui_start()
