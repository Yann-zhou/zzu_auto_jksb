import os
import re

import requests
import logging

from time import sleep
# from requests.packages.urllib3.exceptions import InsecureRequestWarning

from parameter import *
import utils

logging.basicConfig(level=logger_level, format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger('jksb')
# 忽略证书错误
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DEFAULT:@SECLEVEL=1'

# 输出参数状态
logger.info("脚本启动成功！请验证你的信息：")
logger.info("学号：" + username)
logger.info("密码：" + password)
logger.info("省份编号：" + code_province)
logger.info("城市编号：" + code_city)
logger.info("详细位置：" + location)
logger.info("疫苗情况：" + vaccine)
logger.info("经度：" + jingdu)
logger.info("纬度：" + weidu)
logger.info("通知方法：" + send_type)
logger.info("通知参数：" + send_parameter)


def run():
    # 打卡进程
    try:
        logger.info("正在检查是否已经打卡...")
        response_data = utils.get_signin_status()
        if response_data[0] is True and logger_level is not logging.DEBUG:
            logger.info("今日已成功打卡！")
        else:
            # ----------------------------登录后的首个页面----------------------------
            logger.info("今日尚未打卡！")
            logger.info("开始今日打卡进程...")
            did = re.search('(?<=did" value=")[0-9a-zA-Z]*(?=")', response_data[1]).group()
            door = re.search('(?<=door" value=")[0-9a-zA-Z]*(?=")', response_data[1]).group()
            # ghdn28 = re.search('(?<=ghdn28" value=")[0-9a-zA-Z]*(?=")', response_data[1]).group()
            sid1 = re.findall('(?<=sid" value=")[0-9a-zA-Z]*(?=")', response_data[1])[0]
            sid2 = re.findall('(?<=sid" value=")[0-9a-zA-Z]*(?=")', response_data[1])[1]
            men6 = re.search('(?<=men6" value=")[0-9a-zA-Z]*(?=")', response_data[1]).group()
            ptopid = re.search('(?<=ptopid" value=")[0-9a-zA-Z]*(?=")', response_data[1]).group()

            logger.debug("jksb页面中did参数值为："+did)
            logger.debug("jksb页面中door参数值为："+door)
            # logger.debug("jksb页面中ghdn28参数值为："+ghdn28)
            logger.debug("jksb页面中sid1参数值为："+sid1)
            logger.debug("jksb页面中men6参数值为："+men6)
            logger.debug("jksb页面中ptopid参数值为："+ptopid)
            logger.debug("jksb页面中sid2参数值为："+sid2)

            data_jksb_info = {
                'did': did,
                'door': door,
                # 'ghdn28': ghdn28,
                'sid': [sid1, sid2],
                'men6': men6,
                'ptopid': ptopid,
            }
            url_jksb_info = "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb"
            sleep(3)
            logger.info("正在获取打卡页面表单数据...")
            response_data = utils.http.request(method='POST', url=url_jksb_info, body=utils.urlencode(data_jksb_info), headers=header)
            # response_data = requests.post(url=url_jksb_info, data=data_jksb_info, headers=header, verify=False)
            logger.info("成功获取打卡页面表单数据！")
            # ----------------------------提交信息页面----------------------------
            sheng6 = re.search('(?<=sheng6" value=")[0-9a-zA-Z]*(?=")', response_data.data.decode())
            shi6 = re.search('(?<=shi6" value=")[0-9a-zA-Z]*(?=")', response_data.data.decode())
            # ghdn28 = re.search('(?<=ghdn28" value=")[0-9a-zA-Z]*(?=")', response_data.data.decode()).group()
            fun3 = re.search('(?<=fun3" value=")[0-9a-zA-Z]*(?=")', response_data.data.decode())
            ptopid = re.search('(?<=ptopid" value=")[0-9a-zA-Z]*(?=")', response_data.data.decode())
            sid = re.search('(?<=sid" value=")[0-9a-zA-Z]*(?=")', response_data.data.decode())
            # CAPTCHA_url = re.search('(?<=<img src=").*?zzjlogin3d.*?p2p=.*?(?=")', response_data.data.decode())
            # logger.debug("验证码链接为："+CAPTCHA_url.group())
            # logger.debug("页面中ghdn28参数值为："+ghdn28)

            data_jksb = {
                # 'myvs_94c': utils.detect_CAPTCHA(CAPTCHA_url.group()),  # 使用百度API识别验证码
                'myvs_1': '否',  # 1. 您今天是否有发热症状?
                'myvs_2': '否',  # 2. 您今天是否有咳嗽症状?
                'myvs_3': '否',  # 3. 您今天是否有乏力或轻微乏力症状?
                'myvs_4': '否',  # 4. 您今天是否有鼻塞、流涕、咽痛或腹泻等症状?
                'myvs_5': '否',  # 5. 您今天是否被所在地医疗机构确定为确诊病例?
                # 'myvs_6': '否',  # 6. 您今天是否被所在地医疗机构确定为疑似病例?    #已弃用
                'myvs_7': '否',  # 6. 您是否被所在地政府确定为密切接触者?
                'myvs_8': '否',  # 7. 您是否被所在地政府确定为次密切?
                # 'myvs_9': get_zhb_status(),  # 8. **************您昨天是否按要求参加了核酸检测?（此项从郑好办处获取）
                # 'myvs_10': '否',  # 9. 您今天是否被所在地医疗机构进行院内隔离观察治疗?    #已弃用
                'myvs_11': '否',  # 9. 您今天是否被所在地医疗机构进行院内隔离观察治疗?
                'myvs_12': '否',  # 10. 您今天是否被要求在政府集中隔离点进行隔离观察?
                'myvs_13': '否',  # 11. 您今日是否被所在地政府有关部门或医院要求居家隔离观察?
                'myvs_15': '否',  # 12. 共同居住人是否有确诊病例?
                'myvs_13a': code_province,  # **************当前实际所在省份（河南为41）
                'myvs_13b': code_city,  # **************当前实际所在地（请在平台自行查阅地点代码）
                'myvs_13c': location,  # **************当前所在详细地址（自行填写）
                'myvs_24': '否',  # 15. 您是否为当日返郑人员?
                # 'myvs_26': vaccine,  # 16. 您当前疫苗接种情况?（接种一针写1，接种两针写2，未接种写3，有禁忌症未接种写4）
                'memo22': '成功获取',  # 地理位置（此项无需更改）
                'did': '2',
                'door': '',
                'day6': '',
                'men6': 'a',
                'sheng6': sheng6.group() if sheng6 else None,  # 此项从上方返回中找值
                'shi6': shi6.group() if shi6 else None,  # 此项从上方返回中找值
                # 'ghdn28': ghdn28,  # 此项从上方返回中找值
                'fun3': fun3.group() if fun3 else None,  # 此项从上方返回中找值
                'jingdu': jingdu,  # **************此项填所在地经度
                'weidu': weidu,  # **************此项填所在地纬度
                'ptopid': ptopid.group() if ptopid else None,
                'sid': sid.group() if sid else None,
            }
            url_jksb = "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb"
            logger.debug("打卡信息："+str(data_jksb))
            sleep(3)
            logger.info("正在提交打卡信息...")
            response_data = utils.http.request(method='POST', url=url_jksb, body=utils.urlencode(data_jksb), headers=header)
            # response_data = requests.post(url=url_jksb, data=data_jksb, headers=header, verify=False)
            logger.info("提交打卡信息成功！")
            # ----------------------------结果返回页面----------------------------
            logger.info("正在查询打卡结果...")
            sleep(3)
            signin_result = utils.get_signin_status()[0]
            if signin_result is True:
                utils.send_message(re.search('同学.*?(?=<)', response_data.data.decode()).group())
                logger.info("打卡成功！")
            else:
                utils.send_message("打卡失败！网页提示信息为："+str(re.search('(?<=line-height:26px;float:left;">).*?(?=</div><div style="width:10px)', response_data.data.decode()).group()))
                logger.error("打卡失败！网页提示信息为："+str(re.search('(?<=line-height:26px;float:left;">).*?(?=</div><div style="width:10px)', response_data.data.decode()).group()))
    except Exception as err:
        utils.send_message("程序运行异常！错误信息："+str(err))


if __name__ == '__main__':
    run()
