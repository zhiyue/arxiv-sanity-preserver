#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

import redis
import requests
import functools
import logging
import random
from config import *

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


__author__ = 'zhiyue'
__copyright__ = "Copyright 2016"
__credits__ = ["zhiyue"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "zhiyue"
__email__ = "cszhiyue@gmail.com"
__status__ = "Production"


def proxy_config(host="127.0.0.1", port="6379", db=0):
    pool = redis.ConnectionPool(host=host, port=port, db=db)
    redis_conn = redis.StrictRedis(connection_pool=pool)
    key = "ipproxy:1"  # 暂时使用高匿名代理

    def handle_func(func):
        @functools.wraps(func)
        def handle_args(*args, **kwargs):
            return func(*args, **kwargs)

        return functools.partial(handle_args, redis_conn, key)

    return handle_func


@proxy_config(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
def getproxy(redis_conn, key, weight):
    # 根据权重随机获取代理ip, weight : [1...10]
    # 代理IP在redis中以zset存储, weight越大,ip质量越差
    total = redis_conn.zcard(key)
    ips = redis_conn.zrange(key, 0, total / 10 * weight)
    logging.info("ip numbers: %s", len(ips))
    #   获取全部代理IP
    #   ips = r.zrange(key, 0, -1)
    proxies = {
        "http": "http://%s" % ips[random.randint(0, len(ips) - 1)]
    }
    return proxies


def retry(max_retries=RETRY_TIMES, use_proxy=USE_PROXY):
    def handle_func(func):
        @functools.wraps(func)
        def handle_args(*args, **kwargs):
            retries = 0
            while True:
                proxies = None
                if use_proxy:
                    proxies = getproxy(retries + 1)
                    # logging.info(proxies)
                try:
                    # kwargs['proxies'] = proxies
                    func(proxies=proxies, *args, **kwargs)
                    break
                except Exception as e:
                    print e
                logging.error("fail! and %s retrying ", retries)
                retries += 1
                if retries > max_retries:
                    logging.error("fail too many times")
                    break

        return handle_args

    return handle_func


@retry(max_retries=RETRY_TIMES, use_proxy=USE_PROXY)
def download_file(url, local_filename=None, proxies=None, timeout=DOWNLOAD_TIMEOUT, **kwargs):
    if not local_filename:
        local_filename = url.split('/')[-1]
    try:
        logging.info("Proxy: %s and url: %s", proxies, url)
        r = requests.get(url, proxies=proxies, stream=True, timeout=timeout, **kwargs)
        if r.status_code == 200:
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        #                      f.flush() commented by recommendation from J.F.Sebastian
                logging.info("Finish download %s", url)
                #               r.close()
        else:
            logging.error("Error: Unexpected response {}".format(r))
            raise Exception("Unexpected response.")
    except requests.exceptions.RequestException as e:
        # A serious problem happened, like an SSLError or InvalidURL
        logging.error("Error: {}".format(e))
        raise
    except Exception as e:
        logging.error(e)
        raise
