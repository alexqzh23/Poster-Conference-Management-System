import re
from uuid import uuid1
import random
import IPy
#from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

"""
class contain action register and other issues
"""
import string
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send_mail(addr):
    """function for link register to send activate email
    input: email address of receiver(attendee)"""
    # settings for sending email
    s = smtplib.SMTP_SSL('smtp.qq.com', port=465)
    host = 'smtp.qq.com'
    port = 465
    s.connect(host, port)
    mail_user = '2954665643@qq.com' # sender
    mail_pass = 'whaxdbrouciidegc' # authorization code
    s.login(user=mail_user, password=mail_pass) # connect to server
    subject = 'Active your CMS account' # subject of mail
    content = 'Please click the link below to activate your account, \nit will be soon turned to our homepage ' \
              'automatically.\n Please notice that the link will be lose effectiveness in 2 ' \
              'minutes.\nhttp://127.0.0.1:8000/active/{0}'.format(generate_token(addr))
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header("Administrator", 'utf-8')  # sender name
    message['To'] = Header("Attendee", 'utf-8')  # receiver name
    message['Subject'] = Header(subject, 'utf-8')  # subject
    s.sendmail([mail_user], [addr], message.as_string()) #send


def generate_token(addr):
    """generate a token for encrypt the link
    the token generated by secret key 'rho' with email address"""
    SECRET_KEY = 'rho'
    # encryption(key, valid time),
    # for those who want to enter the web again, we set the time as 999999
    s = Serializer(SECRET_KEY, 9999999)
    data = s.dumps(addr)
    token = data.decode()
    return token


def decryption(token):
    """decrypt the activate code from link
    return email address"""
    SECRET_KEY = 'rho'
    serializer = Serializer(SECRET_KEY)
    data = serializer.loads(token)
    return data


def short_uuid():
    """generate unique id by using uuid1, with user's mac address and timestamp"""
    uuid_chars = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                  "k", "l", "m", "n", "o", "p", "q", "r", "s",
                  "t", "u", "v", "w", "x", "y", "z", "0", "1",
                  "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C",
                  "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O",
                  "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
    uuid = str(uuid1()).replace('-', '')
    result = ''
    for i in range(0, 8):
        sub = uuid[i * 4: i * 4 + 4]
        x = int(sub, 16)
        result += uuid_chars[x % 0x3E]
    return result


def generate_posterID():
    """
    used for generating posterID automatically
    """
    return ''.join(random.sample(string.digits, 4))


def generate_pwd():
    """
    used for generating the password for judges
    """
    return ''.join(random.sample(string.ascii_letters + string.digits, 10))


def check_ip(ip):
    """check user's ip address to ensure whether they are in intranet"""
    # check if ip address is valid or not
    comp = re.compile(r'^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
    # Compare whether the IP address is in the UIC intranet segment
    return comp.match(ip) is not None and ip in IPy.IP("172.16.0.0-172.31.255.255")
