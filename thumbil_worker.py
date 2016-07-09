from celery import Celery
app = Celery("__name__", broker='redis://localhost:6379/0', backend="redis://localhost:6379/0")


import os
import os.path
import sys
import time
import shutil
from subprocess import Popen


@app.task
def generate_thumbil(path, outpath):
    p = os.path.basename(path)
    tmpdir = os.path.join('tmp', p)
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    source_pdf = "%s[0-7]" % (path)
    cmd = r'convert %s -thumbnail x156 tmp/%s/test.png' % (source_pdf,p)
    pp = Popen(cmd, shell=True)
    t0 = time.time()
    while time.time() - t0 < 15: # give it 15 seconds deadline
        ret = pp.poll()
        if not (ret is None):
            # process terminated
            break
        time.sleep(0.1)
    ret = pp.poll()
    if ret is None:
        # we did not terminate in 5 seconds
        pp.terminate() # give up

    if not os.path.isfile('tmp/%s/test-0.png' % (p,)):
        # failed to render pdf, replace with missing image
        #os.system('cp %s %s' % ('static/thumbs/missing.jpg', outpath))
        shutil.copyfile('static/thumbs/missing.jpg', outpath)
        print 'could not render pdf, creating a missing image placeholder'
    else:
        cmd = "montage -mode concatenate -quality 80 -tile x1 tmp/%s/test-*.png %s" % (p,outpath)
        os.system(cmd)
    shutil.rmtree('tmp/%s' % (p,))
    time.sleep(0.01)
    return True