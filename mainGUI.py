# -*- coding:utf-8 -*-

from collections import deque

from tkinter import Entry, Label, Button, filedialog, StringVar, Scrollbar, Listbox, Tk, ttk
from tkinter.scrolledtext import ScrolledText
from threading import Thread, Lock

from QGMConf import os, json, DATAPATH, CONFIGS, GROUPPATH, UPDATE_DATE, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_X, WINDOW_Y, messagebox
from mailSender import sender
from spider import crawlQQNum, crawlGroupIds
from utils import logT, dialogMsg, saveConfig, cleanCache


class MyGUI():
    """@brief:使用GUI界面来选择邮箱附件所在的文件夹和邮箱通讯录
    """

    # 构造函数
    def __init__(self, window):
        self.mainWindow = window
        self.gids = []
        self.subject = ''
        self.mail = {'subject': '', 'content': '',
                     'images': [], 'attach': '', 'link': ''}
        self.mails = {}
        self.threadLock = Lock()
        self.count = 0
        self.total = 0
        self.queue = deque()
        self.status = True

    # 初始化窗口
    def set_init_window(self):
        self.mainWindow.title("Pow Mail Tool")  # 设置标题
        posX = int((self.mainWindow.winfo_screenwidth() -
                    WINDOW_WIDTH) / 2 + WINDOW_X)
        posY = int((self.mainWindow.winfo_screenheight() -
                    WINDOW_HEIGHT) / 2 + WINDOW_Y)
        self.mainWindow.geometry(
            f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{posX}+{posY}')  # 设置尺寸
        self.mainWindow.resizable(0, 0)  # 禁止调整大小
        self.mainWindow.attributes('-alpha', 1)  # 属性？

        # 驱动下载地址
        Label(self.mainWindow, text="驱动下载地址: ").grid(
            column=0, row=0, sticky='e')
        a = StringVar()
        Entry(self.mainWindow, textvariable=a, width=50,
              state='readonly').grid(row=0, column=1, columnspan=2, sticky='w')
        a.set('https://npm.taobao.org/mirrors/chromedriver/')

        CLEAN_CACHE_BTN = Button(self.mainWindow,
                                 text='清空缓存',
                                 command=self.cleanLocalCache)
        CLEAN_CACHE_BTN.grid(column=3, row=0)

        BTN_GET_GIDS = Button(self.mainWindow,
                              text='获取群号',
                              command=self.getGids)
        BTN_GET_GIDS.grid(column=1, row=1)

        self.BTN_CRAWL = Button(self.mainWindow,
                                text='获取邮箱',
                                state='disabled',
                                command=self.getMails)
        self.BTN_CRAWL.grid(column=2, row=1)

        self.BTN_READ_MAILS = Button(self.mainWindow,
                                     text='读取邮箱',
                                     state='disabled',
                                     command=self.readMails)
        self.BTN_READ_MAILS.grid(column=3, row=1)

        Label(self.mainWindow, text="选择要发送邮件的群\n(右侧双击删除)",
              padx=10, justify='left').grid(column=0, row=2, sticky='e')
        self.ALL_GIDS = Listbox(
            self.mainWindow, height=5, selectmode='multiple', state='disabled')
        self.ALL_GIDS.grid(column=1, row=2, sticky='wsne')
        self.BTN_CHOSE_GIDS = Button(
            self.mainWindow, text='>>', state='disabled', width=8, command=self.chooseGroup)
        self.BTN_CHOSE_GIDS.grid(column=2, row=2)
        self.CHOOSE_GIDS = Listbox(
            self.mainWindow, height=5, state='disabled')
        self.CHOOSE_GIDS.grid(column=3, row=2, sticky='wsne')
        self.CHOOSE_GIDS.bind(
            '<Double-Button-1>', self.deleteGroup)  # 双击删除gid

        Label(self.mainWindow, text="请输入邮件主题:", padx=10).grid(column=0,
                                                              row=3,
                                                              sticky='e')
        self.MAIL_SUBJECT = Entry(self.mainWindow, state='disabled')
        self.MAIL_SUBJECT.grid(column=1, row=3, columnspan=2, sticky='we')

        Label(self.mainWindow, text="输入邮件内容:", padx=10).grid(column=0,
                                                             row=4,
                                                             sticky='e')
        self.MAIL_CONTENT = ScrolledText(self.mainWindow,
                                         width=70,
                                         height=10,
                                         state='disabled')
        self.MAIL_CONTENT.grid(column=1, row=4, columnspan=3, sticky='w')

        Label(self.mainWindow, text="请输入链接地址:", padx=10).grid(column=0,
                                                              row=5,
                                                              sticky='e')
        self.MAIL_LINK = Entry(self.mainWindow, state='disabled')
        self.MAIL_LINK.grid(column=1, row=5, columnspan=2, sticky='we')

        Label(self.mainWindow, text="选择邮件图片:", padx=10).grid(column=0,
                                                             row=6,
                                                             sticky='e')
        self.MAIL_IMGS = Label(self.mainWindow, text='')
        self.MAIL_IMGS.grid(column=1, row=6, sticky='w')
        self.BTN_MAIL_IMG = Button(self.mainWindow,
                                   text='点击选择',
                                   state='disabled',
                                   command=self.getMailImg)
        self.BTN_MAIL_IMG.grid(column=2, row=6)

        self.BTN_CLEAN_IMGS = Button(self.mainWindow,
                                     text='清空图片',
                                     state='disabled',
                                     command=self._cleanMailImg)
        self.BTN_CLEAN_IMGS.grid(column=3, row=6)

        Label(self.mainWindow, text="选择邮件附件:", padx=10).grid(column=0,
                                                             row=7,
                                                             sticky='e')
        self.MAIL_ATTACH = Label(self.mainWindow, text='')
        self.MAIL_ATTACH.grid(column=1, row=7, sticky='w')
        self.BTN_MAIL_ATTACH = Button(self.mainWindow,
                                      text='点击选择',
                                      state='disabled',
                                      command=self.getMailFile)
        self.BTN_MAIL_ATTACH.grid(column=2, row=7)

        self.BTN_CLEAN_ATTACH = Button(self.mainWindow,
                                       text='清空附件',
                                       state='disabled',
                                       command=self._cleanMailFile)
        self.BTN_CLEAN_ATTACH.grid(column=3, row=7)

        self.BTN_SEND_MAILS = Button(self.mainWindow,
                                     text='群发邮件',
                                     state='disabled',
                                     command=self.sendMails)
        self.BTN_SEND_MAILS.grid(column=1, row=8)

        self.PROGERSS = ttk.Progressbar(
            self.mainWindow, orient="horizontal", length=300, mode="determinate")
        self.PROGERSS.grid(column=2, row=8, columnspan=2)

        self.TIP = Label(text='')
        self.TIP.grid(column=0, row=9, columnspan=4)

        col_count, row_count = self.mainWindow.grid_size()
        for col in range(col_count):
            if col in [1, 3]:
                self.mainWindow.grid_columnconfigure(col, minsize=200)
        for row in range(row_count):
            self.mainWindow.grid_rowconfigure(row, minsize=35)
        self._checkInitState()
        logT('启动程序')

    def _checkInitState(self):
        if UPDATE_DATE != CONFIGS['updateDate']:
            CONFIGS.update({
                'updateDate': UPDATE_DATE,
                'new': True
            })

        if CONFIGS['new']:
            '''第一次打开弹出提示'''
            dialogMsg(m='t')
            CONFIGS['new'] = False
            saveConfig()

        if CONFIGS['sendingGid']:
            '''上次有没发送完的群'''
            dialogMsg(f'群号: {CONFIGS["sendingGid"]}上次发送失败')
            self.gids.append(CONFIGS['sendingGid'])

        if os.path.exists(GROUPPATH) and os.listdir(GROUPPATH):
            self.BTN_READ_MAILS.configure(state='normal')

    def cleanLocalCache(self):
        res = messagebox.askokcancel('警告', '此操作会清空所有本地数据,确定继续?')
        logT('点击清空缓存', 'warn')
        if res:
            cleanCache()
            dialogMsg('为保证程序正常运行,清空数据后会自动关闭本程序。', 'warn')
            logT('清空完成, 重启程序')
            self.mainWindow.quit()
        else:
            logT('取消清空缓存')

    def getGids(self):
        '''扫码获取所有群号'''
        res = crawlGroupIds()
        if res == 0:
            dialogMsg('请确认驱动版本以及是否在本文件夹内', 'err')
        elif res == 1:
            logT(f'获取群号成功: {CONFIGS["gids"]}')
            dialogMsg('获取群号成功')
            self.BTN_CRAWL.configure(state='normal')
        elif res == -2:
            logT('获取失败, 用户未登录')
            dialogMsg('获取失败, 请确认登录')

    def getMails(self):
        if not CONFIGS['gids']:
            logT('没有群号', 'err')
            dialogMsg('请先获取群号', 'err')
            return
        res = crawlQQNum(CONFIGS['gids'])
        if res in [1, -1]:
            msg = '获取邮箱成功'
            if res == -1:
                msg = '此QQ号所有群已爬取完成'
            self.gids.extend(CONFIGS['newCrawled'])
            self.BTN_READ_MAILS.configure(state='normal')
            logT(msg)
            dialogMsg(msg)
        elif res == 0:
            msg = ('获取邮箱失败, 请检查是否成功授权或浏览器和驱动版本是否匹配', 'err')
            logT(*msg)
            dialogMsg(*msg)
        elif res == -2:
            logT('获取失败, 用户未登录')
            dialogMsg('获取失败, 请确认登录')

    def readMails(self):
        try:
            gidFiles = os.listdir(GROUPPATH)
            if gidFiles:
                # CONFIGS['crawledGids'] = gidFiles
                # saveConfig()
                mails = {}
                total = 0
                for gid in gidFiles:
                    with open(os.path.join(GROUPPATH, gid), 'r') as fg:
                        mails[gid] = json.loads(fg.read())
                        total += (len(mails[gid])-1) * \
                            10 + len(mails[gid][-1])
                self.mails = mails
                self._setWidgetState('normal')
                self.ALL_GIDS.delete(0, 'end')
                self.ALL_GIDS.insert('end', *mails.keys())
                if self.gids:
                    self.CHOOSE_GIDS.delete(0, 'end')
                    self.CHOOSE_GIDS.insert('end', *self.gids)
                dialogMsg(f'读取邮箱完成, 共{total}人')
                logT(f'读取邮箱完成, 共{total}人，群号：{gidFiles}')
                return True
            msg = ('没有群邮箱文件在groups文件夹内', 'err')
            logT(*msg)
            dialogMsg(*msg)
        except FileNotFoundError:
            logT('没有groups文件夹', 'err')
            dialogMsg('请先获取邮箱', 'err')

    def chooseGroup(self):
        idxs = self.ALL_GIDS.curselection()
        for idx in idxs:
            gid = self.ALL_GIDS.get(idx)
            if gid not in self.gids:
                logT(f'选择群{gid}')
                self.gids.append(gid)
                self.CHOOSE_GIDS.insert('end', gid)

    def deleteGroup(self, idx):
        gid = self.CHOOSE_GIDS.get('active')
        logT(f'取消选择群{gid}')
        self.CHOOSE_GIDS.delete(0, 'end')
        self.gids.remove(gid)
        self.CHOOSE_GIDS.insert('end', *self.gids)

    def _setWidgetState(self, mode):
        self.ALL_GIDS.configure(state=mode)
        self.BTN_CHOSE_GIDS.configure(state=mode)
        self.CHOOSE_GIDS.configure(state=mode)
        self.MAIL_SUBJECT.configure(state=mode)
        self.MAIL_CONTENT.configure(state=mode)
        self.MAIL_LINK.configure(state=mode)
        self.BTN_MAIL_IMG.configure(state=mode)
        self.BTN_MAIL_ATTACH.configure(state=mode)
        self.BTN_SEND_MAILS.configure(state=mode)

    def getMailFile(self):
        f = filedialog.askopenfilename()
        if f:
            logT(f'添加附件成功 {f}')
            self.mail['attach'] = f
            filename = os.path.split(f)[-1]
            self.MAIL_ATTACH.configure(text=filename)
            self.BTN_CLEAN_ATTACH.configure(state='normal')
        else:
            logT('取消选择附件', 'warn')

    def getMailImg(self):
        img = filedialog.askopenfilename()
        ext = os.path.splitext(img)[-1].lower()
        if img:
            if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                logT(f'添加图片成功 {img}')
                self.mail['images'].append(img)
                imgs = [os.path.split(img)[-1] for img in self.mail['images']]
                self.MAIL_IMGS.configure(text=','.join(imgs))
                self.BTN_CLEAN_IMGS.configure(state='normal')
            else:
                logT('文件类型不正确', 'err')
                dialogMsg('文件类型不正确, 图片仅支持png,jpg,bmp,gif', 'err')
        else:
            logT('取消选择图片', 'warn')

    def _cleanMailImg(self):
        self.mail['images'] = []
        self.MAIL_IMGS.configure(text='')
        logT('清空图片')
        self.BTN_CLEAN_IMGS.configure(state='disabled')

    def _cleanMailFile(self):
        self.mail['attach'] = []
        self.MAIL_ATTACH.configure(text='')
        logT('清空附件')
        self.BTN_CLEAN_ATTACH.configure(state='disabled')

    def _readAccount(self):
        try:
            with open('account.json', 'r') as fa:
                acStr = fa.read()
                try:
                    data = json.loads(acStr)
                    logT(f'成功读取发送者账号')
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
            CONFIGS['sendingGid'] = gid
            saveConfig()
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
            CONFIGS['sendingGid'] = ''
            CONFIGS['sendGids'].append(gid)
            saveConfig()
            self.CHOOSE_GIDS.delete(0, 'end')
            self.gids.remove(gid)
            self.CHOOSE_GIDS.insert('end', *self.gids)
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
        self.mail['subject'] = self.MAIL_SUBJECT.get()
        self.mail['content'] = self.MAIL_CONTENT.get(0.0, 'end')
        self.mail['link'] = self.MAIL_LINK.get()
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
