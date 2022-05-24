# python版本，可根据需求进行修改
FROM python:3.8
RUN mkdir /code
# 将python程序添加到镜像
ADD jksb.py /code/
ADD get_parameter.py /code/
ADD timer.py /code/
ADD tools.py /code/
# 将项目依赖添加到镜像
ADD requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt
# 设置该项以忽略证书错误
RUN sed -i -E 's/MinProtocol[=\ ]+.*/MinProtocol = TLSv1.0/g' /etc/ssl/openssl.cnf

# 调整时间
ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

# 镜像运行时执行的命令，这里的配置等于 python jksb.py
ENTRYPOINT ["python","timer.py"]