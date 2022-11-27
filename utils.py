import requests
import urllib3
from ssl import PROTOCOL_TLSv1_2
import re
from time import sleep
from time import time
from parameter import *
import json
import datetime

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from urllib.parse import quote
from urllib.parse import urlencode

# from PIL import Image
# from io import BytesIO
# from base64 import b64encode

logging.basicConfig(level=logger_level, format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger('jksb_utils')
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
    result = 'y'
    try:
        if zhb_parameter is None:
            return result
        url_zhb = "https://unified-area-code-n-service.jianguan.henan.gov.cn/nucleicapi/nucvac/info"
        data_zhb = '{"param":"'+zhb_parameter+'","_t":'+str(int(time()))+'}'
        header_zhb = {
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/19F77 Ariver/1.1.0 AliApp(AP/10.2.76.6000) Nebula WK RVKType(1) AlipayDefined(nt:4G,ws:375|603|2.0) AlipayClient/10.2.76.6000 Alipay Language/zh-Hans Region/CN NebulaX/1.0.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "unified-area-code-n-service.jianguan.henan.gov.cn",
            "Origin": "https://unified-area-code-zwy.jianguan.henan.gov.cn",
            "Referer": "https://unified-area-code-zwy.jianguan.henan.gov.cn/",
        }

        response_data = requests.post(url=url_zhb, data=data_zhb, headers=header_zhb)
        response_data_json = json.loads(response_data.content.decode())
        report_date = datetime.datetime.strptime(response_data_json["obj"]["nucleicInfo"]["samplingTime"], '%Y-%m-%d %H:%M:%S')
        logger.debug("查询核酸检测结果模块：最新的报告日期为 "+response_data_json["obj"]["nucleicInfo"]["samplingTime"])
        now_date = datetime.datetime.now()
        if (now_date - report_date).days > 1:
            logger.info('郑好办查询结果：昨日未做核酸')
            result = 'x'
        else:
            logger.info('郑好办查询结果：昨日已做核酸')
            result = 'y'
    except Exception as err:
        send_message("郑好办查询失败！")
        logger.error("郑好办查询失败！")
    finally:
        return result


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
            par = json.loads(send_parameter)
            mail_host = par['host']  # 设置服务器
            mail_user = par['user']  # 用户名
            mail_pass = par['password']  # 口令

            sender = par['user']
            receivers = [par['receiver']]
            logger.info(receivers)

            message_mime = MIMEText(message, 'plain', 'utf-8')
            message_mime['From'] = Header(par['user'], 'utf-8')
            message_mime['To'] = Header(par['receiver'], 'utf-8')

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


# # 简单文字识别，现在打卡系统已升级为手写问题，该方法暂时废弃
# def detect_CAPTCHA_ez(url: str):
#     acc_token = json.loads(
#         requests.get(
#             url='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+baidu_API_Key+'&client_secret='+baidu_Secret_Key,
#             headers=header
#         ).text)['access_token']
#
#     CAPTCHA = ""
#     times = 0
#     nums = {"零": 0, "壹": 1, "贰": 2, "叁": 3, "肆": 4, "伍": 5, "陆": 6, "柒": 7, "捌": 8, "玖": 9}
#     while len(CAPTCHA) != 4 and times < 5:
#         CAPTCHA = ""
#         response_data = requests.post(
#             url="https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token="+acc_token,
#             data="url="+url,
#             headers=header)
#         response_json = json.loads(response_data.text)
#         times += 1
#         if response_json["words_result_num"] != 1:
#             continue
#         for i in response_json["words_result"][0]["words"]:
#             if "0" <= i <= "9":
#                 CAPTCHA += i
#             if i in nums:
#                 CAPTCHA += str(nums[i])
#     logger.info("本次打卡验证码为："+CAPTCHA)
#     return CAPTCHA
#
#
# # 手写文字验证码识别
# def detect_CAPTCHA(url: str):
#     CAPTCHA = ""
#     acc_token = json.loads(
#         requests.get(
#             url='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + baidu_API_Key + '&client_secret=' + baidu_Secret_Key,
#             headers=header
#         ).text)['access_token']
#
#     nums = {"零": 0, "壹": 1, "贰": 2, "叁": 3, "肆": 4, "伍": 5, "陆": 6, "柒": 7, "捌": 8, "玖": 9}
#     response_data = requests.post(
#         url="https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token=" + acc_token,
#         data="url=" + url,
#         headers=header)
#     response_json = json.loads(response_data.text)
#     for i in response_json["words_result"][0]["words"]:
#         if "0" <= i <= "9":
#             CAPTCHA += i
#         if i in nums:
#             CAPTCHA += str(nums[i])
#
#     # 如果识别不成功，将图片放大并二值化后再次进行尝试
#     if len(CAPTCHA) != 4:
#         def pil2base64(image):
#             img_buffer = BytesIO()
#             image.save(img_buffer, format='JPEG')
#             byte_data = img_buffer.getvalue()
#             base64_str = b64encode(byte_data)
#             return base64_str
#
#         CAPTCHA = ""
#         img = BytesIO(requests.get(url).content)
#         img = Image.open(img)
#
#         threshold = 183
#         table = []
#         for i in range(256):
#             if i < threshold:
#                 table.append(0)
#             else:
#                 table.append(1)
#         img_base64_urlencode = quote(pil2base64(img.convert('L').resize((880, 220)).point(table, '1')))
#
#         response_data = requests.post(
#             url="https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token=" + acc_token,
#             data="image=" + img_base64_urlencode,
#             headers=header)
#         response_json = json.loads(response_data.text)
#         for i in response_json["words_result"][0]["words"]:
#             if "0" <= i <= "9":
#                 CAPTCHA += i
#             if i in nums:
#                 CAPTCHA += str(nums[i])
#
#     logger.info("本次打卡验证码为：" + CAPTCHA)
#     return CAPTCHA
