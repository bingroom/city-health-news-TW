#-*- coding: utf-8 -*-

import requests
import lxml
import xmltodict
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq
import HTMLParser
import hashlib
from bs4 import BeautifulSoup

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
            content = requests.get(url, timeout=5).content #urllib2.urlopen(url).read()
        except:
            content = None
            print '...retry connection'
            continue    
    return content


def do_pyquery(link, max_retry=3):
    UTF8_PARSER = lxml.html.HTMLParser(encoding='big5')
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
    file_ext = link.rsplit('.')[-1]
    file_path = './files/' + name + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()


PREFIX = 'http://health.tainan.gov.tw/'
#TNN_URL = 'http://health.tainan.gov.tw/tnhealth/news/index.aspx'
TNN_URL = 'https://health.tainan.gov.tw/list.asp?nsub=A0A600&topage=1'


def dump(since_date):
    dl = []

    doc = do_pyquery(TNN_URL)#pq(url=link)
    # print list(doc('div > header').items())
    # import sys
    # sys.exit(0)

    for i in list(doc('div > header').items())[1:]: # pass header
        
        news_date = i('span.post-date > span.day').text()[:9]
        dt = datetime.strptime(news_date, '%Y/%m/%d')
        if dt.date() < since_date:
            break
        date = datetime.strftime(dt, '%Y-%m-%d')
        print date 
        
        #print news_date
        
        news_title = i('#newhead > a').text()
        news_url = PREFIX + i('#newhead > a').attr('href')
        news_doc = do_pyquery(news_url)
        print news_title, news_url
        content = news_doc('div.blogpost-content').text()
        print content
        
        print '---'

        hashcode = hashlib.md5(('tnn'+ news_title + date).encode("utf-8")).hexdigest()
        d = {'url': news_url, 'content': news_title + content, 'date': date, 'hashcode': hashcode}

        dl.append(d)
    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
