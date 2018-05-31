#-*- coding: utf-8 -*-

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

PREFIX = 'http://khd.kcg.gov.tw'
KHH_URL = 'http://khd.kcg.gov.tw/Main.aspx?sn=398'

doc = do_pyquery(KHH_URL)
#print doc('#ListDataPanel').children('table>tr>td')
# for news in doc('#ListDataPanel').children('table>tr>td>a').items():
#     title = news.attr('title')
#     link = news.attr('href')
#     print title, link
#     print '---'
news_table = list(doc('#ListDataPanel').children('table>tr').items())
for news in news_table[1:]:
    news_date = news('td').eq(0).text()
    ad_year = str(int(news_date.split('/')[0]) + 1911)
    news_date = ad_year + '/' + news_date.split('/', 1)[-1]
    dt = datetime.strptime(news_date, '%Y/%m/%d')
    if dt < datetime(2017, 5, 10):
        break
    title = news('td>a').attr('title')
    link = PREFIX + news('td>a').attr('href')
    print news_date
    print title, link
    news_doc = do_pyquery(link)
    print news_doc('#DataViewContent').text()
    print '@attach:'
    for f in news_doc('#AttachmentPanel>ul>li>a').items():
        file_name = f.attr('title')
        file_url = PREFIX + f.attr('href')
        file_url = urllib2.quote(file_url.encode('utf-8'), safe=':/')
        #print file_url
        download_file(file_url, file_name)
    print '---'