
import csv
import requests

def iterate_companies():
    txt = requests.get('http://www.asx.com.au/asx/research/ASXListedCompanies.csv').text
    return txt
    c = csv.reader(txt)
    return c
    for name, code, industry in c:
        if industry == 'Materials':
            print(code)
