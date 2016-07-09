# -*- coding: utf-8 -*-
# @Author: zhiyue
# @Date:   2016-06-19 00:42:17
# @Last Modified by:   zhiyue
# @Last Modified time: 2016-06-19 01:54:09
from celery import Celery
import wget
import time
import random

app = Celery(__name__, broker='redis://localhost:6379/0', backend="redis://localhost:6379/0")


@app.task
def download(pdf_url, path):
    wget.download(pdf_url, path)
    time.sleep(0.1 + random.uniform(0, 0.2))
    return True
