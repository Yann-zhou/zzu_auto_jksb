# ZZU_auto_jksb


## 项目简介

该项目可以帮助你自动进行每日健康上报，项目使用python作为后台，只需简单配置即可自动运行，后续准备添加docker与Github Actions支持

## 使用方法
1. 将以下值加入系统环境变量
```
jksb_username           健康上报系统中的用户名
jksb_password           健康上报系统中的密码
jksb_code_province      当前所在省份代码（河南为41）
jksb_code_city          当前所在城市代码（郑州为4101）
jksb_location           当前所在地详细地址
jksb_vaccine            疫苗接种情况
jksb_jingdu             当前所在地经度
jksb_weidu              当前所在地纬度
jksb_send_type          后续通知方法类型（可选bark,serverchan,email）
jksb_send_parameter     根据send_type进行选择，
                        send_type为bark与serverchan时，该项为推送URL，
                        send_type为serverchan时，该项为SCT开头的sendkey
                        send_type为email时，该项格式为：{"host": "smtp服务器地址", "user": "邮箱登录名", "password": "邮箱密码", "receiver": "接收邮件的邮箱"}
jksb_zhb_parameter      郑好办核酸检测查询抓包内容，留空则默认将“昨天是否进行过核酸检测”项填写为“做了”
jksb_logger_level       日志等级
```
2. 调用jksb.py中的run方法即可运行

## ~~待添加功能~~
- [x] 自动采集郑好办核酸检测信息(不稳定)
- [x] docker支持
- [x] Github Actions支持