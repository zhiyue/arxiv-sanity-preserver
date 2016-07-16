#!/usr/bin/env python
# -*- coding: utf-8 -*-
from celery_app import app
import shutil
import time
import os
import logging
from subprocess import Popen
import random

from dowload import download_file
# app.config_from_object('config')

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


@app.task
def download(pdf_url, path):
    if os.path.exists(path):
        return True
    download_file(pdf_url, path)
    time.sleep(0.1 + random.uniform(0, 0.2))
    return True


@app.task
def transform(pdf_path, txt_path):
    cmd = "pdftotext %s %s" % (pdf_path, txt_path)
    os.system(cmd)
    if not os.path.isfile(txt_path):
        with open(txt_path, 'w') as fin:
            pass
    time.sleep(0.02)  # silly way for allowing for ctrl+c termination
    return True


@app.task
def generate_thumbil(path, outpath):
    p = os.path.basename(path)
    tmpdir = os.path.join('tmp', p)
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    source_pdf = "%s[0-7]" % (path, )
    cmd = r'convert %s -thumbnail x156 tmp/%s/test.png' % (source_pdf, p)
    pp = Popen(cmd, shell=True)
    t0 = time.time()
    while time.time() - t0 < 15:  # give it 15 seconds deadline
        ret = pp.poll()
        if not (ret is None):
            # process terminated
            break
        time.sleep(0.1)
    ret = pp.poll()
    if ret is None:
        # we did not terminate in 5 seconds
        pp.terminate()  # give up

    if not os.path.isfile('tmp/%s/test-0.png' % (p,)):
        shutil.copyfile('static/thumbs/missing.jpg', outpath)
        logger.error('%s could not render pdf, creating a missing image placeholder' % (p,))
    else:
        cmd = "montage -mode concatenate -quality 80 -tile x1 tmp/%s/test-*.png %s" % (p, outpath)
        os.system(cmd)
    shutil.rmtree('tmp/%s' % (p,))
    time.sleep(0.01)
    return True
