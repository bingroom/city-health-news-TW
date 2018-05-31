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
FILE_PREFIX = 'http://www.ylshb.gov.tw/'
PREFIX = 'http://www.ylshb.gov.tw/news/'
YUN_URL = 'http://www.ylshb.gov.tw/news/index.php?m=9&m1=14&m2=35'

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
    file_path = './files/' + name.split('.')[0] + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    dl = []
    doc = do_pyquery(YUN_URL)
    tbl = list(doc('.T14.color01>table').children('tr').items())
    for i in tbl[1:-1:2]: #doc('.T14.color01>table').children('tr').eq(1).items():
        news_date = i('td').eq(2).text()
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        if dt.date() < since_date:
            break

        news_title = i('td').eq(1).text()
        
        news_url = PREFIX + i('td').eq(1)('a').attr('href')
        #print news_date, news_title, news_url
        news_doc = do_pyquery(news_url)
        content = news_doc('table>tr>td.T14.color01').text().split(u'附加檔案：')[0].strip()#.remove('p').remove('a').text()
        #print news_doc('table>tr>td.T14.color01').text()
        # s = str(news_doc('table>tr').find('td.T14.color01'))
        # from BeautifulSoup import BeautifulStoneSoup
        #decoded = BeautifulStoneSoup(s, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        #print decoded
        #print news_doc('table>tr').find('td.T14.color01')
        #news_doc('table>tr').find('td.T14.color01').remove('p').remove('a').text()
        
        print content
        if u'附加檔案：' in news_doc('table>tr').find('td.T14.color01').text():
            print '@attach:'
            file_name = news_doc('a.link-text').text()
            file_url = FILE_PREFIX + news_doc('a.link-text').attr('href').split('/', 1)[-1]
            print file_name, file_url
            download_file(file_url, file_name)

        print '----'

    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
