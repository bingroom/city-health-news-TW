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
FILE_PREFIX = 'http://www.phchb.gov.tw/'
PREFIX = 'http://www.phchb.gov.tw/'
#PEH_URL = 'http://www.phchb.gov.tw/ch/home.jsp?mserno=201110060008&serno=201203280001&contlink=ap/unitdata.jsp'
PEH_URL = 'https://www.phchb.gov.tw/home.jsp?id=23'
#PEH_URL = 'https://www.phchb.gov.tw/home.jsp?id=38'

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
    doc = do_pyquery(PEH_URL)
    #content > tbody > tr:nth-child(3) > td > table:nth-child(1) > tbody > tr:nth-child(1) > td:nth-child(3) > a
    
    #print list(doc('div.con > div').items())

    for i in doc('div.con > div').items():#.eq(2)('td.table').items():
        news_date = i('span').eq(0).text()
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        #print news_date
        if dt.date() < since_date:
            break
        news_url = PREFIX + i('a').attr('href')#PREFIX + i('tr>td').eq(2)('a').attr('href')
        news_title = i('a').attr('title')#i('tr>td').eq(2)('a').text()
        print news_date
        print news_title, news_url
        #news_url = 'http://www.phchb.gov.tw/ch/home.jsp?mserno=201110060008&serno=201110060010&contlink=ap/news_view.jsp&dataserno=201707050001'
        news_doc = do_pyquery(news_url)
        print news_doc('#centent > div.sub > ul > li.con').text()#news_doc('#content > tr').eq(2)('td.text').text()
        
        print '@attach:'
        #print news_doc('span.icon').items()
        #break
        file_len = sum(1 for _ in news_doc('span.icon').items())
        #print file_len
        #continue
        for f in range(0, file_len):
            file_doc = news_doc('span.icon').children().eq(f)
            file_name = news_doc('span.icon').eq(f).attr('title')
            file_url = FILE_PREFIX + file_doc.attr('href')
        #     if file_doc.find('td.text>a'):
        #         file_name = file_doc('td.text>a').attr('title')
        #         file_url = FILE_PREFIX + file_doc('td.text>a').attr('href')
            #print file_name, file_url
            download_file(file_url, file_name)
            print '@@@'
        print '--'
        #break

    return dl
if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
