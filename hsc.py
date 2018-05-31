#-*- coding: utf-8 -*-
import lxml.html
import urllib2
import requests
import xmltodict
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq
import hashlib
#from libs import file_to_text
import os
import shutil

FILES_DIR = './files/'
PREFIX = 'http://health.tainan.gov.tw/'
FILE_PREFIX = 'http://www.hccg.gov.tw/'
HSC_URL = 'http://www.hccg.gov.tw/MunicipalNews?websitedn=ou=hcchb,ou=ap_root,o=hccg,c=tw&language=chinese&title=%E8%A1%9B%E7%94%9F%E6%96%B0%E8%81%9E'

class pp(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf-8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


def get_content(url, max_retry=10):
    content = None
    retry = 0
    while content == None:
        try:
            retry += 1
            if retry == max_retry:
                content = None
                break
            content = requests.get(url).content #urllib2.urlopen(url).read()
        except:
            content = None
            print '...retry connection'
            continue    
    return content


def do_pyquery(link, max_retry=10):
    UTF8_PARSER = lxml.html.HTMLParser(encoding='utf-8')
    doc = None
    retry = 0
    while doc == None:
        try:
            retry += 1
            if retry >= max_retry:
                break
            doc = pq(lxml.html.fromstring(get_content(link), parser=UTF8_PARSER))
    
        except: 
            doc = None
            print '...retry doing pyquery'
            continue
    return doc


def is_attachment(link):
    ext_list = ['pdf', 'jpg', 'jpeg', 'doc', 'docx', 'ppt', 'pptx', 'xsl', 'xslx']
    ignore_files = ['qrcode.jpg']
    link_ext = link.rsplit('.')[-1]
    link_file = link.rsplit('/')[-1] 
    if link_file not in ignore_files and link_ext.lower() in ext_list:
        return True
    else:
        return False


def download_file(link, name):
    #print link, name
    file_content = get_content(link)
    if file_content == None:
        return
    file_ext = link.rsplit('.')[-1]
    file_path = './files/' + name + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    
    req = get_content(HSC_URL)
    xml_dict = xmltodict.parse(req)
    
    #news_dict = {}
    dl = []
    for i in xml_dict['rss']['channel']['item']:         
        dt = datetime.strptime(i['pubDate'], '%a, %d %b %Y %H:%M:%S %Z')
        if dt.date() < since_date:#datetime(2017, 5, 28).date(): #datetime.today()
            break
        
        title = i['title']
        link = PREFIX + i['link']
        content = i['description']
        print dt
        print title, link
        print content
        print '----'

    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
