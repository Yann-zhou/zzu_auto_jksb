import datetime
import time
import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler


def run_jksb():
    import jksb


if __name__ == '__main__':
    schedular = BlockingScheduler()
    schedular.add_job(run_jksb, "cron", second=50, jitter=5)
    schedular.add_job(run_jksb, "cron", second=30, jitter=20)
    schedular.start()