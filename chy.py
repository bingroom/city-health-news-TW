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
import dateutil.parser

FILES_DIR = './files/'
PREFIX = 'https://cyshb.cyhg.gov.tw/'
#CHY_URL = 'http://www.cyshb.gov.tw/11activity/news.asp'
CHY_URL = 'https://cyshb.cyhg.gov.tw/News.aspx?n=E236E03D6AE796F8&sms=A55ECAF6D99EACF8'

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
            content = requests.get(url, timeout=5).content #urllib2.urlopen(url).read()
        except:
            content = None
            print '...retry connection'
            continue    
    return content

def do_pyquery(link, max_retry=3):
    UTF8_PARSER = lxml.html.HTMLParser(encoding='big5')
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
    file_ext = link.rsplit('.')[-1]
    file_path = './files/' + name + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    dl = []
    doc = do_pyquery(CHY_URL)

    #html/body/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[4]/td/table/tbody/tr[2]/td/table/tbody/tr[2]
    #html>body>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr
    #print doc('.t').text()
    #print doc("#movie-table")
    tbl = list(doc("#movie-table > tbody > tr").items())
    #tbl = list(doc(u"table[summary='新聞稿區總覽']>tr").items())

    for i in tbl[0:]:#doc(u"table[summary='新聞稿區總覽']>tr").items():
        

        news_date = i('td > p').eq(0).text()
        #print news_date
        ad_year = str(int(news_date.split('-')[0]) + 1911)
        news_date = ad_year + '-' + news_date.split('-', 1)[-1]
        #news_date = "{0:4d}/{1:02d}/{2:02d}".format(*[int(x) for x in news_date.split('/')])
        dt = datetime.strptime(news_date, '%Y-%m-%d')

        #print news_date.split('/')
        #print "{0:4s}/{1:02s}/{2:02s}".format(news_date.split('/'))#dateutil.parser.parse(news_date)
        
        if dt.date() < since_date:
            break
        date = datetime.strftime(dt, '%Y-%m-%d')
        print date 
        
        news_title = i('td > p > a').attr('title')#i('td').eq(0)('a').text()
        news_url = PREFIX + i('td > p > a').attr('href')#i('td').eq(0)('a').attr('href')
        print news_title, news_url
        news_doc = do_pyquery(news_url)

        content = news_doc('#data_midlle > div').eq(3).text()
        #print news_doc("p[align='left']").text()
        #print list(news_doc('td > div > ol').items())
        file_len = sum(1 for _ in news_doc('td > div > ol').items())
        #print file_len
        for f in range(file_len):
            file_doc = news_doc('td > div > ol > li').eq(f)
            #print file_doc
            file_url = file_doc('li > span > a').attr('href')
            #print file_url
            if file_url != None:
                print '@attach:'
                file_url = file_url
                file_name = file_doc.text()
                print file_name, file_url
                download_file(file_url, file_name)
        print '--'
        #break
    # for i in doc('#pageRight > div.pageContainer > ul').children().items():
    #     news_date = i('li').text().split('|')[0].strip()
    #     print news_date
    #     dt = datetime.strptime(news_date, '%Y-%m-%d')
    #     if dt.date() < since_date:
    #         break
    #     news_url = PREFIX + i('a').attr('href')
    #     news_title = i('a').attr('title')
        
    #     print news_title, news_url 
    #     #news_url = 'http://www.chshb.gov.tw/news/index.php?mode=data&id=12395&type_id=127'
    #     news_doc = do_pyquery(news_url)
    #     content = news_doc('#content').text()
    #     print content
    #     #print news_doc('#pageContainer>table>tr>')
    #     if u'附加檔案' in news_doc('#pageContainer>table>tr>th').text():
    #         print '@attach:'
    #         file_url = FILE_PREFIX + news_doc('#pageContainer>table>tr>td>a').attr('href')
    #         file_name = news_doc('#pageContainer>table>tr>td>a').text()
    #         print file_url, file_name
    #         download_file(file_url, file_name)
    #     print '--'
        #break

        hashcode = hashlib.md5(('chy'+ news_title + date).encode("utf-8")).hexdigest()
        d = {'url': news_url, 'content': news_title + content, 'date': date, 'hashcode': hashcode}

        dl.append(d)

    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
