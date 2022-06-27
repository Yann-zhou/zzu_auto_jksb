import requests
import urllib3
from ssl import PROTOCOL_TLSv1_2
import re
from time import sleep
from get_parameter import *
import json
import datetime

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from urllib.parse import quote
from urllib.parse import urlencode

logging.basicConfig(level=logger_level, format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger('jksb_tools')
urllib3.disable_warnings()
http = urllib3.PoolManager(cert_reqs='CERT_NONE', ssl_version=PROTOCOL_TLSv1_2)
# requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions)
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DEFAULT:@SECLEVEL=1'


# 获取打卡状态的方法
def get_signin_status():
    data_login = {
        'uid': username,  # 此处填学号
        'upw': password,  # 此处填密码
        'smbtn': '进入健康状况上报平台',
        'hh28': '937'     # 该参数作用未知，保持默认值不变
    }
    sleep(3)
    r = http.request(method='POST', url=url_login, body=urlencode(data_login), headers=header)
    # r = requests.post(url=url_login, data=data_login, headers=header, verify=False)
    logger.debug("检查打卡状态模块：已获取login页返回值")
    try:
        ptopid = re.search('(?<=ptopid=).*?(?=&)', r.data.decode()).group()
        sid = re.search('(?<=sid=).*?(?=")', r.data.decode()).group()
    except TypeError:
        logger.error("获取打卡状态时出错：login的response中无ptopid或sid")
    sleep(3)
    r = http.request(method='GET', url='https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid='+ptopid+'&sid='+sid+'&fun2=', headers=header)
    # r = requests.get(url='https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid='+ptopid+'&sid='+sid+'&fun2=')
    logger.debug("检查打卡状态模块：jksb页面返回值：ptopid="+ptopid+", sid="+sid)
    # 计算返回网页中对号的数量，为8则打卡成功，其他情况均未打卡成功
    if r.data.decode().count('ok2020.png') == 8:
        logger.info("打卡状态：已打卡")
        return [True, r.data.decode()]
    else:
        logger.info("打卡状态：未打卡")
        return [False, r.data.decode()]


# 获取郑好办核酸检测信息的方法
def get_zhb_status():
    try:
        if zhb_parameter is None:
            return 'y'
        url_zhb = "https://check-report.z.digitalcnzz.com:5443/hs-check-result/check/result/queryWithToken"
        data_zhb = zhb_parameter.encode('utf-8')
        header_zhb = {
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/19E258 ChannelId(3) NebulaSDK/1.8.100112 Nebula izzzwfwapp zhenghaoban/4.0.0 WK PSDType(1) mPaaSClient/11",
            "Accept": "application/json, text/plain, */*",
            "Host": "check-report.z.digitalcnzz.com:5443",
            "Origin": "https://cdn.digitalcnzz.com",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Authorization": "M7ZWXjmQrNEOIlRYYobnPEnK0mnhdfwC",
            "Referer": "https://cdn.digitalcnzz.com/",
        }

        response_data = requests.post(url=url_zhb, data=data_zhb, headers=header_zhb)
        response_data_json = json.loads(response_data.content.decode())
        report_date = datetime.datetime.strptime(response_data_json['data']['resultList'][0]['reportTime'], '%Y-%m-%d %H:%M:%S')
        logger.debug("查询核酸检测结果模块：最新的报告日期为 "+response_data_json['data']['resultList'][0]['reportTime'])
        now_date = datetime.datetime.now()
        if (now_date - report_date).days > 0:
            logger.info('郑好办查询结果：昨日未做核酸')
            return 'x'
        else:
            logger.info('郑好办查询结果：昨日已做核酸')
            return 'y'
    except:
        send_message("郑好办查询失败！")
        logger.error("郑好办查询失败！")
    finally:
        return 'y'


# 发送通知的方法
def send_message(message: str):
    if send_type == 'bark':
        if send_parameter[-1] != '/':
            http.request(method='GET', url=send_parameter + '/健康打卡/' + message)
        else:
            http.request(method='GET', url=send_parameter + '健康打卡/' + message)
        logger.info("已使用"+send_type+"模式发送消息“"+message+"”")

    elif send_type == 'serverchan':
        http.request(method='GET', url='https://sctapi.ftqq.com/' + send_parameter + '.send?title=' + quote(message))
        logger.info("已使用"+send_type+"模式发送消息“"+message+"”")

    elif send_type == 'email':
        # send_parameter应为json字符串，格式为：{"host": "smtp服务器地址", "user": "邮箱登录名", "password": "邮箱密码", "receiver": "接收邮件的邮箱"}
        try:
            parameter = json.loads(send_parameter)
            mail_host = parameter['host']  # 设置服务器
            mail_user = parameter['user']  # 用户名
            mail_pass = parameter['password']  # 口令

            sender = parameter['user']
            receivers = [parameter['receiver']]
            logger.info(receivers)

            message_mime = MIMEText(message, 'plain', 'utf-8')
            message_mime['From'] = Header(parameter['user'], 'utf-8')
            message_mime['To'] = Header(parameter['receiver'], 'utf-8')

            message_mime['Subject'] = Header("健康上报结果", 'utf-8')

            smtp_obj = smtplib.SMTP_SSL(mail_host, 465)
            smtp_obj.login(mail_user, mail_pass)
            smtp_obj.sendmail(sender, receivers, message_mime.as_string())
            logger.info("已使用"+send_type+"模式发送消息“"+message+"”")
        except smtplib.SMTPException:
            logger.error('无法发送邮件')
        except json.decoder.JSONDecodeError:
            logger.critical("邮件参数异常！")
    else:
        logger.warning('未设置通知方法，待通知消息为：' + message)

