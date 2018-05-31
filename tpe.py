#-*- coding: utf-8 -*-
import urllib2
import requests
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq
import json
import os
import shutil
import hashlib
#from libs import file_to_text
import urllib3
urllib3.disable_warnings()
import lxml

FILES_DIR = './files/'
PREFIX = 'http://health.gov.taipei'
POSTFIX = '&tabid=36&mid=442'
TPE_URL = 'https://health.gov.taipei/Default.aspx?tabid=36&mid=442'


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
            if retry >= max_retry:
                content = None
                break
            content = requests.post(url, verify=False).content #$requests.get(url).content #urllib2.urlopen(url).read()
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

def download_file(link, name):
    file_content = get_content(link)
    if file_content == None:
        return
    file_ext = link.rsplit('&tabid=36&mid=442')[0].rsplit('.')[-1]
    file_path = './files/' + name + '.' + file_ext
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    doc = do_pyquery(TPE_URL)
    tbl = list(doc('#dnn_ctr442_MainView_AnnouncementsMore_dgdMoreList').children().items())
    for i in tbl[2:]:
        if i('td').eq(3).text().strip() != u'食品':
            continue
        news_date = i('td').eq(5).text()
        dt = datetime.strptime(news_date, '%Y/%m/%d')
        if dt.date() < since_date:
            break
        #print news_date
        news_title = i('a').text()#.text()#('tr>td').eq(1)
        news_url = PREFIX + i('a').attr('href')
        print news_title

        news_doc = do_pyquery(news_url)#pq(url=link)
        content = news_doc('.ModuleDescription').text()
        print content
        print '@attach:'
        for f in news_doc('#dnn_ctr442_MainView_AnnouncementsDetail_dstAppendix>span>span>a').items():
            file_name = f.text()
            file_url = PREFIX + f.attr('href')
            print file_name , file_url
            #print file_name, file_url
            #download_file(file_url, file_name)

        print '---'

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    dl = dump(since_date)
    #pp().pprint(dl)
