#-*- coding: utf-8 -*-

import urllib2
import xmltodict
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq
import HTMLParser
from bs4 import BeautifulSoup
import time
import requests

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
            content = requests.get(url).content #urllib2.urlopen(url).read()
            
        except:
            content = None
            print '...retry connection'
            time.sleep(0.5)
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
    #print len(file_content)
    if file_content == None:
        print 'fail on: ', link
        return
    file_ext = link.rsplit('.')[-1]
    raw_name = name

    if name in uniq_count:   
        uniq_count[name] += 1
        name = '%s(%d)' % (name, uniq_count[name])
    else:
        uniq_count[name] = 0

    file_path = './files/' + raw_name # + '.' + file_ext
    if 'jpg' in link.lower():
        file_path += '.jpg'

    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()


PREFIX = 'http://dph.tycg.gov.tw/'
TYC_URL = 'http://dph.tycg.gov.tw/home.jsp?id=13'

doc = do_pyquery(TYC_URL)
#print doc('#ListDataPanel').children('table>tr>td')
# for news in doc('#ListDataPanel').children('table>tr>td>a').items():
#     title = news.attr('title')
#     link = news.attr('href')
#     print title, link
#     print '---'
#news_data = list(doc('.dashed').children('tr').items())
news_data = doc('.text_04')
#fout = open('attach_list.txt', 'wb')
for i in news_data.items():
    news_date = i('td').eq(3).text()
    ad_year = str(int(news_date.split('-')[0]) + 1911)
    news_date = ad_year + '-' + news_date.split('-', 1)[-1]
    dt = datetime.strptime(news_date, '%Y-%m-%d')
    #if dt.date() < datetime(2017, 5, 24).date():
    #    break
    print news_date
    title = i('td > a').attr('title')
    link = PREFIX + i('td > a').attr('href')

    print title, link
    news_doc = do_pyquery(link)
    print '@attach:'
    for f in news_doc('.pubupload>a').items():
        file_name = f.text()
        file_url = f.attr('href').strip()
        print file_name, file_url
        #fout.write(file_name.encode('utf-8')+'\t'+file_url+'\n')
        download_file(file_url, file_name)


#http://www.tycg.gov.tw/uploaddowndoc?file=health1/201705181634010.pdf&filedisplay=1060518%E6%96%B0%E8%81%9E%E7%A8%BF%28%E6%AD%A3%E9%9C%B2%E4%B8%B8%29.pdf&flag=doc
    print '@img:'
    for img in news_doc('.img_border').items():
        img_name = img.attr('alt')
        img_url = img.attr('src')
        print img_name, img_url
        download_file(img_url, img_name)
    print '---'
    #break
#fout.close()