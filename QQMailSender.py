import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os


def _authLogin(email, auth):
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    try:
        server.login(email, auth)
        return server
    except:
        return


def _withImg(imgPath, msg):
    # 添加图片
    file = open(imgPath, "rb")
    img_data = file.read()
    file.close()

    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'imageid')
    msg.attach(img)
    return msg


def _withFile(filePath, msg):
    att = MIMEText(open(filePath, 'rb').read(), 'base64', 'gb2312')
    att["Content-Type"] = 'application/octet-stream'
    att.add_header('Content-Disposition',
                   'attachment',
                   filename=os.path.split(filePath)[-1])
    msg.attach(att)
    return msg


def sender(email,
         auth,
         subject,
         receivers,
         content,
         imgPath=None,
         filePath=None):
    server = _authLogin(email, auth)
    if not server:
        return '登陆失败, 请检查邮箱和授权码'
    message = MIMEMultipart('related')
    message['Subject'] = subject
    message['From'] = email
    message['To'] = ','.join(receivers)
    content = MIMEText(f'<html><body>{content}</body></html>', 'html', 'utf-8')
    # content = MIMEText(
    #     '<html><body><img src="cid:imageid" alt="imageid"></body></html>', 'html', 'utf-8')
    message.attach(content)

    if imgPath:
        message = _withImg(imgPath, message)
    if filePath:
        message = _withFile(filePath, message)

    # 发送邮件
    try:
        server.sendmail(email, receivers, message.as_string())
        server.quit()
        return "邮件成功发送给%d个人" % len(receivers)
    except smtplib.SMTPException as e:
        print(e)
        return "发送失败, 请切换QQ或稍后再试"


if __name__ == '__main__':
    sender('767710688@qq.com', 'ojosjwekknupbbha', 'test mail',
         ['2855829886@qq.com'], 'hello world\naaaaa\nwori')
