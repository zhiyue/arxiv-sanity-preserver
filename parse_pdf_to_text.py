"""
Very simple script that simply iterates over all files pdf/f.pdf
and create a file txt/f.pdf.txt that contains the raw text, extracted
using the "pdftotext" command. If a pdf cannot be converted, this
script will not produce the output file.
"""

import logging
import os

from tasks import transform

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


if not os.path.exists('txt'):
    os.makedirs('txt')

have = set(os.listdir('txt'))
files = os.listdir('pdf')
for i, f in enumerate(files, start=1):
    pdf_path = os.path.join('pdf', f)
    txt_basename = f + '.txt'
    txt_path = os.path.join('txt', txt_basename)
    if txt_basename not in have:
        cmd = "pdftotext %s %s" % (pdf_path, txt_path)
        transform.delay(pdf_path, txt_path)
        logger.info('%d/%d %s' % (i, len(files), cmd))
    else:
        logger.info('skipping %s, already exists.', pdf_path)
