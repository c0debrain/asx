
OUTDIR = '/data/asx/mining_contracts_full'
import csv
from datetime import datetime
import logging
import mechanize
import os
import re
import sys

# I really tried to switch, but mechanize only supports py2
assert sys.version_info.major ==2 

logging.basicConfig(level=logging.DEBUG)

# each line looks something like
# ACS,2014,14/03/2014,0,Half Year Accounts,16,http://www.asx.com.au/asx/statistics/displayAnnouncement.do?display=pdf&idsId=01501203,http://www.asx.com.au/asx/statistics/displayAnnouncement.do?display=pdf&idsId=01501203

def dl_lines(lineiterator):
    reader = csv.reader(lineiterator)
    br = mechanize.Browser()
    for line in reader:
        company = line[0]
        year = datetime.strptime(line[2], '%d/%m/%Y')
        pdfurl = line[6]
        assert (len(line) < 8) or line[7].strip() == '' #we don't have any extracted text
        pdfid = re.search('\d+$', pdfurl).group(0)
        company_dir = '%s/%s' % (OUTDIR, company)
        if not os.path.exists(company_dir): os.makedirs(company_dir)
        outfile = '%s/%s_%s_%s.pdf' % (company_dir, company, year.strftime('%Y-%m-%d'), pdfid)
        if os.path.exists(outfile):
            logging.debug('skipping already-downloaded doc %s' % outfile)
            continue
        with open(outfile, 'wb') as fh:
            logging.debug('processing %s' % outfile)
            resp = br.open(pdfurl)
            if resp.info()['Content-type'] != 'application/pdf':
                # we are on the terms of use page
                br.select_form(nr=0)
                resp=br.submit(nr=1)
            assert(resp.info()['Content-type'] == 'application/pdf')
            fh.write(resp.read())
            pass # need to navigate a form
        

def test():
    lines = ['ACS,2014,14/03/2014,0,Half Year Accounts,16,http://www.asx.com.au/asx/statistics/displayAnnouncement.do?display=pdf&idsId=01501203,']
    return dl_lines(lines)
    
if __name__ == '__main__':
    dl_lines(sys.stdin)
