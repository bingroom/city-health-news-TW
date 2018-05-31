#-*- coding: utf-8 -*-
import lxml.html
import urllib2
import requests
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq
import hashlib
import os
import shutil
#from libs import file_to_text

FILES_DIR = './files/'
PREFIX = 'http://www.hlshb.gov.tw/'
HWA_URL = 'http://www.hlshb.gov.tw/files/40-1006-27-1.php'

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
            content = requests.get(url, timeout=20).content #urllib2.urlopen(url).read()
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
    file_ext = name.rsplit('.')[-1]
    raw_name = name.rsplit('.')[0]
    file_path = './files/' + raw_name + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    dl = []
    doc = do_pyquery(HWA_URL)
    for i in doc('div.md_middle > div > div > div > table > tbody > tr').items():
        news_date = i('td').eq(2).text()#.encode('utf-8')
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        #if dt.date() < since_date:
        #    break
        news_url = i('td').eq(1)('a').attr('href')
        if PREFIX not in news_url:
            continue
        
        news_title = i('td').eq(1).text()
        news_doc = do_pyquery(news_url)
        print news_date, news_title
        
        content = news_doc('div.ptcontent.clearfix.floatholder').remove('.itemattr').text()
        print '--'

    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
