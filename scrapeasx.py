

# it must be time for this by now
import sys
assert sys.version_info.major >= 3


import os
import csv
import urllib.request
import urllib.parse
import requests
import lxml.html

OUTDIR = '/data/asx/mining'
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)

def iterate_companies(industry_segment='Materials'):
    txt = requests.get('http://www.asx.com.au/asx/research/ASXListedCompanies.csv')
    for line in csv.reader(txt.text.split('\r\n')):
        if len(line) != 3:
            continue
        if line[2] == industry_segment:
            yield line

def get_filings_list(asx, minyear=2010, maxyear=2015):
    for year in range(maxyear, minyear-1, -1):
        url = 'http://www.asx.com.au/asx/statistics/announcements.do?by=asxCode&asxCode=%s&timeframe=Y&year=%s' % (asx, year)
        yield (year, url)


def filings_for_company(asx):
    outfile = '%s/%s.csv' % (OUTDIR, asx)
    if os.path.exists(outfile):
        print('skipping already-scraped %s' % outfile)
        return
    with open(outfile, 'w') as outfh:
        writer = csv.writer(outfh)
        for (year, url) in get_filings_list(asx, minyear=2000):
            newfilings = list(filings_page(url, asx, year))
            if len(newfilings) == 0 and year < 2015:
                print('breaking %s at year %s' % (asx, year))
                return
            for line in newfilings:            
                writer.writerow(line)
    

def filings_page(url, asx=None, year=None):
    text = requests.get(url).text
    doc = lxml.html.fromstring(text)
    for row in doc.cssselect('table.contenttable>tbody tr'):
        tds = row.findall('td')
        texts = [x.text_content().strip() for x in tds]
        paid = tds[1].find('img') is not None
        pdfurl, texturl = '', ''

        try:
            pdfurlfrag = tds[4].find('a').attrib['href']
            pdfurl = urllib.parse.urljoin(url, pdfurlfrag)
        except AttributeError:
            pass

        try:
            texturlfrag = tds[5].find('a').attrib['href']
            texturl = urllib.parse.urljoin(url, texturlfrag)
        except AttributeError:
            pass

        yield([
            asx,
            year,
            texts[0], # filing date
            1 if paid else 0,
            texts[2], # headline
            texts[3], # pagecount
            pdfurl,
            texturl,
        ])            


def run():
    for (name,code,industry) in iterate_companies():
        print('processing %s' % code)
        filings_for_company(code)

if __name__ == '__main__':
    run()
                      
    

