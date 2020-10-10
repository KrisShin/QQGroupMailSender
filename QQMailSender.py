import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def _authLogin(email, auth):
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    try:
        server.login(email, auth)
        return server
    except:
        return


def send(email, auth, subject, receivers, content, attaches=None):
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

    # 添加图片
    # file = open("test.png", "rb")
    # img_data = file.read()
    # file.close()

    # img = MIMEImage(img_data)
    # img.add_header('Content-ID', 'imageid')
    # message.attach(img)

    try:
        server.sendmail(email, receivers, message.as_string())
        server.quit()
        return "邮件成功发送给%d个人" % len(receivers)
    except smtplib.SMTPException as e:
        print(e)
        return "发送失败, 请切换QQ或稍后再试"


if __name__ == '__main__':
    send('767710688@qq.com', 'ojosjwekknupbbha', 'test mail',
         ['2855829886@qq.com'], 'hello world\naaaaa\nwori')
