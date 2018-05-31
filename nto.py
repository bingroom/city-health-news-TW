#-*- coding: utf-8 -*-
import lxml.html
import urllib2
import requests
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq
import hashlib
#from libs import file_to_text
import os
import shutil

FILES_DIR = './files/'
FILE_PREFIX = 'https://www.ntshb.gov.tw'
PREFIX = 'https://www.ntshb.gov.tw/news/'
NTO_URL = 'https://www.ntshb.gov.tw/news/index.aspx?type=0&aid=4'

class pp(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf-8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


def get_content(url, max_retry=3):
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
            import traceback
            print traceback.print_exc()
            content = None
            print '...retry connection'
            continue    
    return content

def do_pyquery(link, max_retry=3):
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
    dl = []
    doc = do_pyquery(NTO_URL)
    #print doc.text()
    #print doc('.list.left > div > a') 
    #import sys
    #sys.exit(0)
    for i in doc('.list.left > a').items():
        news_date = i('a > div').eq(0).text()
        dt = datetime.strptime(news_date, '%Y.%m.%d')
        if dt.date() < since_date:
            break
        news_url = PREFIX + i('a').attr('href')
        news_title = i('a').attr('title')
        news_doc = do_pyquery(news_url)
        print dt.date()
        print news_title, news_url
        #print news_doc('#section>div').eq(2)('table>tr').eq(1).text() # remove dup title in content
        content = news_doc('div.Ad-4.tabs.left > table > tr').eq(1).text()
        
        print '@attach:'
        files_doc = news_doc('#section>div').eq(2)('table>tr>td.n-sty.file-icon')
        for f in files_doc.children().items():
            file_url = FILE_PREFIX + f('a').attr('href')
            file_name = f('a').text()
            print file_name, file_url
            download_file(file_url, file_name)
        print '---'

        date = datetime.strftime(dt, '%Y-%m-%d')
        ut = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        hashcode = hashlib.md5(('nto' + news_title + news_date).encode("utf-8")).hexdigest()
        d = {'url': news_url, 'content': news_title + content, 'date': news_date, 'updatetime': ut, 'hashcode': hashcode}
    
    return dl
if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
