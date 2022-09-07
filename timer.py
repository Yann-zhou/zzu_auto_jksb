import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from parameter import jksb_timer, logger_level
import jksb
import logging

logging.basicConfig(level=logger_level, format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger('jksb_timer')


def run_jksb():
    jksb.run()


if __name__ == '__main__':
    schedular = BlockingScheduler()
    time_list = eval(jksb_timer)
    for idt, t in enumerate(time_list):
        schedular.add_job(run_jksb, "cron", hour=t[0], minute=t[1], jitter=t[2])
        logger.info("已添加第"+str(idt+1)+"个计划任务，预计在"+str(t[0])+"时"+str(t[1])+"分打卡，随机偏移量为"+str(t[2])+"秒")
    schedular.start()
