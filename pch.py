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
PREFIX = 'http://www.ptshb.gov.tw/'
PCH_URL = 'http://www.ptshb.gov.tw/News.aspx?CategorySN=1894&n=CC774672B906BC5E'

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
            #content = requests.get(url, timeout=20).content #urllib2.urlopen(url).read()
            content = urllib2.urlopen(url).read()
        
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
    file_ext = name.rsplit('.')[-1]
    raw_name = name.rsplit('.')[0]
    file_path = './files/' + raw_name + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    dl = []
    doc = do_pyquery(PCH_URL)
    #print doc
    #text = str(doc)
    #print text
    #from bs4 import BeautifulSoup
    #print BeautifulSoup(text, 'lxml')
    #print doc
    #import sys
    #sys.exit(0)
    for i in doc('.css_tr>tr').not_('.css_title').items():
        news_date = i("td[align='center']").text()
        ad_year = str(int(news_date.split('/')[0]) + 1911)
        news_date = ad_year + '/' + news_date.split('/', 1)[-1]
        dt = datetime.strptime(news_date, '%Y/%m/%d')
        if dt.date() < since_date:
            break
        news_title = i('a').text()
        news_url = PREFIX + i('a').attr('href')
        file_name = i('a').attr('title')
        print news_date
        print news_title, news_url
        if file_name == None:
            
            news_doc = do_pyquery(news_url)
            content = news_doc('#ContentPlaceHolder1_divContent').text()
            print content

            print '@attach:'
            for f in news_doc('.news_box03_data>ol>li>ul>li>a').items():
                file_url = f.attr('href')
                file_name = f.attr('title')
                print file_url, file_name
                download_file(file_url, file_name)

        else:
            content = []
            print content
            file_name = file_name.split(u'(另開視窗)')[0]
            file_url = news_url
            print '@attach:'
            print file_url, file_name
            download_file(file_url, file_name)

        print '--'

    return dl

if __name__ == '__main__':
    since_date = datetime(2018, 5, 20).date()
    pp().pprint(dump(since_date))
