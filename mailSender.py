import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from utils import randSleep, logT, dialogMsg

SLEEPTIME = 5  # 实际等待时间是5秒
MAILTPS = {
    'qq': ('smtp.qq.com', 465),
    '163': ('smtp.163.com', 465),
    '126': ('smtp.126.com', 25),
}


def _authLogin(email, auth, mailType):
    server = smtplib.SMTP_SSL(*MAILTPS[mailType])
    try:
        server.login(email, auth)
        logT(f'{email}登录成功')
        return server
    except:
        msg = (f'{email} 登陆失败, 请检查邮箱和授权码', 'err')
        logT(*msg)
        dialogMsg(*msg)
        return


def _withImg(imgsPath, msg):
    '''Add images'''
    for i, imgPath in enumerate(imgsPath):
        with open(imgPath, "rb") as fi:
            img_data = fi.read()
            img = MIMEImage(img_data)
            img.add_header('Content-ID', f'imageid{i}')
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
    message = MIMEMultipart('related')
    message['Subject'] = mail['subject']
    message['From'] = email
    message['To'] = ','.join(receivers)
    text = mail['content']
    # content = MIMEText(f'<html><body>{content}</body></html>', 'html', 'utf-8')
    for i in range(len(mail['images'])):
        imgContent += f'<div><img src="cid:imageid" alt="imageid{i}"></div>'
    content = MIMEText(
        f'<html><body><pre>{text}</pre>{imgContent}</body></html>',
        'html', 'utf-8')
    message.attach(content)

    if mail['images']:
        message = _withImg(mail['images'], message)
    if mail['attach']:
        message = _withFile(mail['attach'], message)
    return message


def sender(email, auth, mailType, receivers, mail, num=0):
    server = _authLogin(email, auth, mailType)
    if not server:
        return '登陆失败, 请检查邮箱和授权码'

    msg = _compContent(email, receivers, mail)

    # 发送邮件
    try:
        server.sendmail(email, receivers, msg.as_string())
        server.quit()
        logT(f"邮件成功发送给{num}个人, 3到7秒后刷新")
        randSleep(3, 7)
        return len(receivers)
    except smtplib.SMTPException as e:
        print(e)
        return


if __name__ == '__main__':
    # sender('767710688@qq.com', 'ojosjwekknupbbha', 'test mail',
    #        ['2855829886@qq.com'], 'hello world\naaaaa\nwori')
    pass
