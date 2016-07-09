# -*- coding: utf-8 -*-
# @Author: zhiyue
# @Date:   2016-06-19 16:28:44
# @Last Modified by:   zhiyue
# @Last Modified time: 2016-06-19 16:52:27

from celery import Celery

import cPickle as pickle
import urllib2
import shutil
import time
import os
import random


app = Celery("__name__", broker='redis://localhost:6379/0',
             backend="redis://localhost:6379/0")


@app.task
def transform(pdf_path, txt_path):
    cmd = "pdftotext %s %s" % (pdf_path, txt_path)
    os.system(cmd)
    if not os.path.isfile(txt_path):
        with open(txt_path, 'w') as fin:
            pass
    time.sleep(0.02) # silly way for allowing for ctrl+c termination
    return True
