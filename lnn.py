#-*- coding: utf-8 -*-
import urllib2
import requests
import xmltodict
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq
import lxml
import json
import os
import shutil
import hashlib
#from libs import file_to_text
import urllib3
urllib3.disable_warnings()


FILES_DIR = './files/'
FILE_PREFIX = 'http://www.matsuhb.gov.tw/'
PREFIX = 'http://www.matsuhb.gov.tw/2009web/news/'
INN_URL = 'http://www.matsuhb.gov.tw/2009web/news/news_contents.php?room=news1'
 

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
            content = requests.get(url, timeout=20).content#requests.post(url, verify=False).content #$requests.get(url).content #urllib2.urlopen(url).read()
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
    #file_ext = link.rsplit('&tabid=36&mid=442')[0].rsplit('.')[-1]
    file_path = './files/' + name# + '.' + file_ext
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):

    dl = []
    doc = do_pyquery(INN_URL)

    #print doc('.dashed-bottom9')
    for i in doc(u"table[summary=新聞列表]").children().items():
        news_date = i('td').eq(0).text()[1:-1]
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        if dt.date() < since_date:
            break
        news_url = PREFIX + i('td').eq(1)('a').attr('href')
        news_title = i('td').eq(1)('a').attr('title')
        print news_date, news_title, news_url
        #news_url = 'http://www.matsuhb.gov.tw/2009web/news/news_detail.php?room=news1&id=2360'
        news_doc = do_pyquery(news_url)
        content = news_doc('.dashed-bottom5').text()
        if u'相關連結：':
            content = content.split(u'相關連結：')[0].strip()
        #print content
        print '@attach:'
        for f in news_doc('tr>td>a').items():
            file_url = FILE_PREFIX + f.attr('href')
            file_url = file_url.replace('../', '')
            file_name = f.siblings().text()

            print file_url, file_name
            print '@@'
            download_file(file_url, file_name)
        #break
        # try:
        #     print PREFIX+i('a').attr('href')
        # except Exception as e:
        #     #raise e
        #     continue
        # title=i('a').attr('title')
        # print title
        print '-----'
        #break

    #tbl = list(doc('#dnn_ctr442_MainView_AnnouncementsMore_dgdMoreList').children().items())

    
    
    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 6, 10).date()
    city_dict = dump(since_date)
    pp().pprint(city_dict)
