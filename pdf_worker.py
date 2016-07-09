# -*- coding: utf-8 -*-
# @Author: zhiyue
# @Date:   2016-06-19 00:42:17
# @Last Modified by:   zhiyue
# @Last Modified time: 2016-06-21 17:23:33
from celery import Celery
import wget
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
    if os.path.exists(path) and os.path.getsize(path) > 10*1024**2:
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
    retries = 0
    while True:
        proxies = getproxy(retries + 1)
        #proxies = None
        try:
            #r = requests.get(url, proxies=proxies, timeout=timeout)
            r = requests.get(url, proxies=proxies, stream=True, timeout=timeout)
            if r.status_code == 200:
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=4096):
                       if chunk: # filter out keep-alive new chunks
                           f.write(chunk)
                            #f.flush() commented by recommendation from J.F.Sebastian
                    print url
                    #r.close()
                    break
                #     r.raw.decode_content = True
                #     shutil.copyfileobj(r.raw, f)
                #     r.close()
                #     break
            else:
                raise Exception("networ error.")
        except Exception as e:
            print e
        print "fail! and retrying..."
        retries += 1
        if retries > 10:
            print "fail too many times"
            break






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
