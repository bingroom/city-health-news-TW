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
PREFIX = 'http://www.ttshb.gov.tw/'
TTT_URL = 'http://www.ttshb.gov.tw/files/40-1000-12-1.php?Lang=zh-tw'

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
    file_ext = name.rsplit('.')[-1]
    raw_name = name.rsplit('.')[0]
    file_path = './files/' + raw_name + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    dl = []
    doc = do_pyquery(TTT_URL)
    for i in doc('#Dyn_2_2 > div > div.md_middle > div > div > div > table > tr > td.mc').items():#.children('td.mc').items():
        news_date = i('span.date.float-right').text()
        news_date = news_date[news_date.find('[')+1:news_date.find(']')].strip()
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        if dt.date() < since_date:
            break
        news_url = i('span.ptname>a').attr('href')
        if PREFIX not in news_url:
            continue
        news_title = i('span.ptname>a').text()
        print news_date, news_title
        #news_url = 'http://www.ttshb.gov.tw/files/14-1000-1257,r12-1.php?Lang=zh-tw'
        news_doc = do_pyquery(news_url)
        content = news_doc('div.ptcontent').remove('.itemattr').text()
        print content
        
        for f in news_doc('#Dyn_2_2 > div > div > div >div >div.mm_01> table.baseTB>tr').items():
            if f.find('a'):
                print '@attach:'
                file_name = f('td>div>span').eq(1)('a').text()
                file_url = PREFIX + f('td>div>span').eq(1)('a').attr('href')
                print file_name, file_url
                download_file(file_url, file_name)
            #print '@@'
        #print news_doc()
        print '--'
        #break

    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
