# -*- coding: utf-8 -*-
import os
import pickle

from tasks import download

if not os.path.exists('pdf'):
    os.makedirs('pdf')


numok = 0
numtot = 0
db = pickle.load(open('db.p', 'rb'))
have = set(os.listdir('pdf'))  # get list of all pdfs we already have
for pid, j in db.iteritems():

    pdfs = [x['href'] for x in j['links'] if x['type'] == 'application/pdf']
    assert len(pdfs) == 1
    pdf_url = pdfs[0] + '.pdf'
    basename = pdf_url.split('/')[-1]
    fname = os.path.join('pdf', basename)
    numtot += 1
    if basename not in have:
        print 'fetching %s into %s' % (pdf_url, fname)
        download.delay(pdf_url, fname)
        numok += 1
    else:
        print '%s exists, skipping' % (fname, )

    print '%d/%d of %d add to download tasks.' % (numok, numtot, len(db))

print 'final number of papers downloaded okay: %d/%d' % (numok, len(db))
