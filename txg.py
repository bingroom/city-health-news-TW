#-*- coding: utf-8 -*-

import urllib2
import xmltodict
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq
import HTMLParser
import requests
import hashlib
#from libs import file_to_text
import os
import shutil

FILES_DIR = './files/'
PREFIX = 'http://www.health.taichung.gov.tw/'
TXG_URL = 'http://www.health.taichung.gov.tw/26216/26204/26216/26204/26201/26204/27056/Lpsimplelist'


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
            content = requests.get(url).content #urllib2.urlopen(url).read()
        except:
            content = None
            print '...retry connection'
            continue    
    return content


def do_pyquery(link, max_retry=10):
    doc = None
    retry = 0
    while doc == None:
        try:
            retry += 1
            if retry == max_retry:
                break
            doc = pq(url=link)
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
    doc = do_pyquery(TXG_URL)

    #print list(doc('#center > section.list > ul > li').items())
    #import sys
    #sys.exit(0)
    dl = []

    for i in list(doc('#center > section.list > ul > li').items())[1:]:
        news_date = i("a > span").eq(1).text()
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        if dt.date() < since_date:
            break
        news_title = i('a').attr('title')
        news_url = PREFIX + i('a').attr('href')
        file_name = i('a').attr('title')
        print news_date
        print news_title, news_url
        news_doc = do_pyquery(news_url)#pq(url=link)
        #print news_doc.text()
        content = news_doc('#cpArticle').text()
        
        file_len = sum(1 for _ in news_doc('#center > section.attachment > ul > li').items())
        #print list(news_doc('#center > section.attachment > ul > li').items())
        print file_len
        for f in range(file_len):
            file_doc = news_doc('#center > section.attachment > ul > li').eq(f)
            file_url = file_doc('a').attr('href')
            print file_url
            if file_url != None:
                print '@attach:'
                file_url = PREFIX + file_url
                file_name = file_doc('a').text()
                print file_name, file_url
                download_file(file_url, file_name)
        print '---'
        
        # attach_doc = doc('section[class="cp"]')

        # if os.path.exists(FILES_DIR):
        #    shutil.rmtree(FILES_DIR)
        # os.makedirs(FILES_DIR)
        # files = []
        # for pdf in attach_doc('a').items():
        #     href = pdf.attr('href')
        #     if '.jpg' not in href:
        #         file_url = PREFIX + href
        #         if is_attachment(file_url):
        #             file_name = pdf.attr('title')
        # for img in attach_doc('img').items():
        #     files.append(PREFIX + img.attr('src'))
        #     file_url = PREFIX + img.attr('src')
        #     if is_attachment(file_url):
        #         file_name = img.attr('alt')
        #         download_file(file_url, file_name)
        

        # files_content = file_to_text(FILES_DIR)


        date = datetime.strftime(dt, '%Y-%m-%d')
        ut = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        hashcode = hashlib.md5(('txg' + news_title + news_date).encode("utf-8")).hexdigest()
        d = {'url': news_url, 'content': news_title + content, 'date': news_date, 'updatetime': ut, 'hashcode': hashcode}

        dl.append(d)

    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 4, 28).date()
    city_dict = dump(since_date)
    pp().pprint(city_dict)