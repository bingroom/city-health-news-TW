#-*- coding: utf-8 -*-

#########

# NOTE: 公告沒照日期排...

#########

import urllib2
import xmltodict
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq
import HTMLParser
from bs4 import BeautifulSoup

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
            content = urllib2.urlopen(url).read()
        except:
            content = None
            print '...retry connection'
            continue    
    return content


def do_pyquery(link, max_retry=10):
    doc = None
    retry = 10
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
    file_ext = link.rsplit('.')[-1]
    file_path = './files/' + name + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

PREFIX = 'http://www.klchb.gov.tw/ch/news/newspaper/'
FILE_PREFIX = 'http://www.klchb.gov.tw/'
KLU_URL = 'http://www.klchb.gov.tw/ch/news/newspaper/list.aspx?c0=640'

doc = do_pyquery(KLU_URL)
#print doc('#ListDataPanel').children('table>tr>td')
# for news in doc('#ListDataPanel').children('table>tr>td>a').items():
#     title = news.attr('title')
#     link = news.attr('href')
#     print title, link
#     print '---'
news_data = list(doc('.GridTable').children('tr').items())
for i in news_data[1:]:
    news_date = i('.GridTD1').text()
    dt = datetime.strptime(news_date, '%Y/%m/%d')

    if dt.date() < datetime(2017, 2, 1).date():
        break
    #print i.text()
    title = i('.grida').text()

    link = PREFIX + i('.grida').attr('href')
    print title, link
    news_doc = do_pyquery(link)
    print news_doc('.Content').text()
    print '@attach:'
    for f in news_doc('.MContent').find('a').items():
        file_url = FILE_PREFIX + f.attr('href').rsplit('../')[-1]
        if 'KLCHB/_uploadS' in file_url:
            file_name = file_url.rsplit('/')[-1]
            if '.' in file_name:
                file_name = file_name.rsplit('.', 1)[0]
            file_url = urllib2.quote(file_url.encode('utf-8'), safe=':/')
            if is_attachment(file_url):
                #if '' in f(''):
                
                if 'jpg' in file_url.lower() and f('img').attr('alt') != None:
                    file_name = f('img').attr('alt')
                print file_name
                print file_url
                download_file(file_url, file_name)
                
                #download_file(file_url, file_name)
    print '---'