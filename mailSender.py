import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from QGMConf import os
from utils import randSleep, logT, dialogMsg

MAILTPS = {
    'qq': 'smtp.qq.com',
    '163': 'smtp.163.com',
    '126': 'smtp.126.com',
}


def _authLogin(email, auth, mailType):
    server = smtplib.SMTP_SSL(MAILTPS[mailType], 465)
    try:
        server.login(email, auth)
        logT(f'{email}登录成功')
        return server
    except Exception as e:
        print(e)
        msg = (f'{email} 登陆失败, 请检查邮箱和授权码', 'err')
        logT(*msg)
        return False


def _withImg(imgsPath, msg):
    '''Add images'''
    for i, imgPath in enumerate(imgsPath):
        with open(imgPath, "rb") as fi:
            img_data = fi.read()
            img = MIMEImage(img_data)
            img.add_header('Content-ID', f'imageid_{i}')
            msg.attach(img)
    return msg


def _withFile(filePath, msg):
    '''
    @func: 邮件添加附件
    @params: filePath - 附件路径
             msg      - 邮件信息流对象
    @return: msg      - 邮件信息流对象
    '''
    att = MIMEText(open(filePath, 'rb').read(), 'base64', 'gb2312')
    att["Content-Type"] = 'application/octet-stream'
    att.add_header('Content-Disposition',
                   'attachment',
                   filename=os.path.split(filePath)[-1])
    msg.attach(att)
    return msg


def _compContent(email, receivers, mail):
    message = MIMEMultipart()
    message['Subject'] = mail['subject']
    message['From'] = email
    message['To'] = ','.join(receivers)
    text = mail['content']
    imgContent, link = '',''
    for i in range(len(mail['images'])):
        imgContent += f'<div><a href="www.bing.com"><img src="cid:imageid_{i}" /></a></div>'
    if mail['link']:
        link = '<a href="{}" >{}</a>'.format(mail['link'], mail['link'])
    content = MIMEText(
        f'<html><body><pre>{text}</pre>{link}{imgContent}</body></html>',
        'html', 'utf-8')
    message.attach(content)

    if mail['images']:
        message = _withImg(mail['images'], message)
    if mail['attach']:
        message = _withFile(mail['attach'], message)
    return message


def sender(email, auth, mailType, receivers, mail):
    server = _authLogin(email, auth, mailType)
    if not server:
        return 0

    msg = _compContent(email, receivers, mail)

    # 发送邮件
    try:
        server.sendmail(email, receivers, msg.as_string())
        server.quit()
        randSleep(3, 6)
        return len(receivers)
    except smtplib.SMTPException as e:
        logT(f'{email} 发送邮件失败, 原因请查看日志'+e, 'err')
        dialogMsg(f'{email} 发送邮件失败, 原因请查看日志')
        return -1


if __name__ == '__main__':
    # ojosjwekknupbbha 767710688@qq.com
    # slkgzjxcalcidded 2855829886@qq.com
    sender('2855829886@qq.com', 'slkgzjxcalcidded', 'qq',
           ['767710688@qq.com'],
           {'subject': 'hello', 'content': 'ahahaha',
            'images': [ r'D:\Projects\pycode\QQGroupMail\tutorail.png', r'D:\Projects\pycode\QQGroupMail\tutorail.png'], 
            'attach': r'D:\Projects\pycode\QQGroupMail\tutorail.png', 
            'link': 'www.bing.com'})
    pass
