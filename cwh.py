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
FILE_PREFIX = 'http://www.chshb.gov.tw/'
PREFIX = 'http://www.chshb.gov.tw/news/'
CWH_URL = 'http://www.chshb.gov.tw/news/?type_id=127&top=0'

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
            content = requests.get(url, timeout=5).content #urllib2.urlopen(url).read()
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
    dl = []
    doc = do_pyquery(CWH_URL)
    for i in doc('#pageRight > div.pageContainer > ul').children().items():
        news_date = i('li').text().split('|')[0].strip()
        print news_date
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        if dt.date() < since_date:
            break
        news_url = PREFIX + i('a').attr('href')
        news_title = i('a').attr('title')
        
        print news_title, news_url 
        #news_url = 'http://www.chshb.gov.tw/news/index.php?mode=data&id=12395&type_id=127'
        news_doc = do_pyquery(news_url)
        content = news_doc('#content').text()
        print content
        #print news_doc('#pageContainer>table>tr>')
        if u'附加檔案' in news_doc('#pageContainer>table>tr>th').text():
            print '@attach:'
            file_url = FILE_PREFIX + news_doc('#pageContainer>table>tr>td>a').attr('href')
            file_name = news_doc('#pageContainer>table>tr>td>a').text()
            print file_url, file_name
            download_file(file_url, file_name)
        print '--'
        #break


    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
