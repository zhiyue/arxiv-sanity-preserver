# -*- coding: utf-8 -*-
# @Author: zhiyue
# @Date:   2016-06-19 00:42:17
# @Last Modified by:   zhiyue
# @Last Modified time: 2016-06-19 15:00:36
from celery import Celery
#import wget
import time
import random
import urllib2
import shutil
import os
import requests
import redis
import py_wget

app = Celery("__name__", broker='redis://localhost:6379/0', backend="redis://localhost:6379/0")

pool = redis.ConnectionPool(host="192.168.1.32", port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)
key = "ipproxy:1"   # 暂时使用高匿名代理
timeout = 20        # 连接超时

@app.task
def download(pdf_url, path):
    if os.path.exists(path):
        return True
    #req = urllib2.urlopen(pdf_url, None, 10)
    #with open(path, 'wb') as fp:
    #   shutil.copyfileobj(req, fp)
    download_file(pdf_url, path)
    time.sleep(0.1 + random.uniform(0, 0.2))
    return True


def download_file(url, local_filename):
    #local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    wget = py_wget.wget()
    wget.download_use_proxy(url, local_filename)





def getproxy(weight):
    # 根据权重随机获取代理ip, weight : [1...10]
    # 代理IP在redis中以zset存储, weight越大,ip质量越差
    total = r.zcard(key)
    ips = r.zrange(key, 0, total/10*weight)
    # 获取全部代理IP
    # ips = r.zrange(key, 0, -1)
    proxies = {
        "http": "http://%s" % ips[random.randint(0, len(ips)-1)]
    }
    return proxies
