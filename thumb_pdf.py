# use imagemagick to convert
# them all to a sequence of thumbnail images
# requires sudo apt-get install imagemagick


import logging
import os.path

from tasks import generate_thumbil

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

if not os.path.exists('static/thumbs'):
    os.makedirs('static/thumbs')

if not os.path.exists('tmp'):
    os.makedirs('tmp')

relpath = "pdf"
allFiles = os.listdir(relpath)
pdfs = [x for x in allFiles if x.endswith(".pdf")]

for i, p in enumerate(pdfs):
    fullpath = os.path.join(relpath, p)
    outpath = os.path.join('static', 'thumbs', p + '.jpg')

    if os.path.isfile(outpath):
        logger.info('skipping %s, exists.' % (fullpath,))
        continue

    logger.info("%d/%d processing %s" % (i, len(pdfs), p))
    generate_thumbil.delay(fullpath, outpath)
