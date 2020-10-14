import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os, time

SLEEPTIME = 5  # 实际等待时间是5秒


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


def _compContent(email, subject, receivers, content, imgPath, filePath):
    message = MIMEMultipart('related')
    message['Subject'] = subject
    message['From'] = email
    message['To'] = ','.join(receivers)
    # content = MIMEText(f'<html><body>{content}</body></html>', 'html', 'utf-8')
    content = MIMEText(
        f'<html><body><div>{content}</div><img src="cid:imageid" alt="imageid"></body></html>',
        'html', 'utf-8')
    message.attach(content)

    if imgPath:
        message = _withImg(imgPath, message)
    if filePath:
        message = _withFile(filePath, message)
    return message


def sender(email,
           auth,
           subject,
           receivers,
           content,
           TIP2,
           num,
           imgPath=None,
           filePath=None):
    server = _authLogin(email, auth)
    if not server:
        return '登陆失败, 请检查邮箱和授权码'

    msg = _compContent(email, subject, receivers, content, imgPath, filePath)

    # 发送邮件
    try:
        server.sendmail(email, receivers, msg.as_string())
        server.quit()
        for i in range(SLEEPTIME, -1, -1):
            TIP2.configure(text=f"邮件成功发送给{num}个人, {i}秒后刷新")
            time.sleep(1)
        return len(receivers)
    except smtplib.SMTPException as e:
        print(e)
        return


if __name__ == '__main__':
    # sender('767710688@qq.com', 'ojosjwekknupbbha', 'test mail',
    #        ['2855829886@qq.com'], 'hello world\naaaaa\nwori')
    pass
