#-*- coding: utf-8 -*-

#########

# NOTE: 內文是直接從doc複製貼上，很多header字(新聞稿..發文日期..之類)
# 沒附件、有照片

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
    url = urllib2.quote(url.encode('utf-8'), safe=':/?&=')
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


uniq_count = {}
def download_file(link, name):
    #print link, name
    file_content = get_content(link)
    file_ext = link.rsplit('.')[-1]
    
    if name in uniq_count:   
        uniq_count[name] += 1
        name = '%s(%d)' % (name, uniq_count[name])
    else:
        uniq_count[name] = 0

    file_path = './files/' + name + '.' + file_ext
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

PREFIX = 'http://www.ilshb.gov.tw'
ILC_URL = 'http://www.ilshb.gov.tw/index.php?catid=23&cid=4'

doc = do_pyquery(ILC_URL)
#print doc('#ListDataPanel').children('table>tr>td')
# for news in doc('#ListDataPanel').children('table>tr>td>a').items():
#     title = news.attr('title')
#     link = news.attr('href')
#     print title, link
#     print '---'
#news_data = list(doc('.dashed').children('tr').items())
news_data = list(doc(u'table#cnt_table[summary="訊息專區列表"]').children('tr').items())
for i in news_data[1:]:
    news_date = i('td').eq(0).text()
    dt = datetime.strptime(news_date, '%Y-%m-%d')
    if dt.date() < datetime(2017, 2, 28).date():
        break

    link = PREFIX + '/' + i('td>a').attr('href')
    title = i('td>a').attr('title')
    print title, link
    news_doc = do_pyquery(link)
    print news_doc(u'table#cnt_table[summary="排版表格"]').children('tr').eq(2).text()
    content_doc = news_doc(u'table#cnt_table[summary="排版表格"]').children('tr').eq(2)
    print content_doc.text()
    print '@attach:'
    for img in content_doc.find('img').items():
        #print 
        img_name = img.attr('title')
        img_link = PREFIX + img.attr('src')
        if img_name == None:
            img_name = img_link.rsplit('/')[-1].split('.')[0]
        print img_name, img_link
        download_file(img_link, img_name)
    print '---'