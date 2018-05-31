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
import urllib3
urllib3.disable_warnings()

FILES_DIR = './files/'
FILE_PREFIX = 'https://www.mlshb.gov.tw/tc/'
PREFIX = 'https://www.mlshb.gov.tw/'
MAL_URL = 'https://www.mlshb.gov.tw/tc/PressRelease.aspx?pn=1&department=7'

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
            content = requests.post(url, verify=False).content #requests.get(url).content #urllib2.urlopen(url).read()
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
    #file_ext = name.rsplit('.')[-1]
    file_path = './files/' + name# + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    dl = []
    doc = do_pyquery(MAL_URL)
    for i in doc('#news_box>ul').children().items():
        news_date = i('i>span').text()
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        if dt.date() < since_date:
            break
        news_title = i('h3').text()
        news_url = PREFIX + i('a').attr('href')
        #news_url = 'https://www.mlshb.gov.tw/tc/PressReleaseContent.aspx?id=1629&chk=956c1771-1c4e-49a4-b3a1-b115bb56c4fa&mid=15&param=pn%3d4%26department%3d7%26key%3d'
        print news_title
        news_doc = do_pyquery(news_url)
        print news_doc('.txtDetail').remove('h3').text() # remove dup title in content
        for f in news_doc('#ctl00_content_ucMoreFiles_rptList_ctl00_hlLink').items():
            file_url = FILE_PREFIX + f('a').attr('href') 
            file_name = f('a').attr('title').split('(', 1)[0].strip()
            download_file(file_url, file_name)
        print '----'
        #break
    #for i in doc('#ctl00_content_rptList_ctl00_hlLink'):
    #    print i('a').attr('href')
    #    print i('i>span').text()

    return dl
if __name__ == '__main__':
    since_date = datetime(2017, 4, 27).date()
    pp().pprint(dump(since_date))
