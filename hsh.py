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
#from libs.file_to_text import file_to_text

FILES_DIR = './files/'
PREFIX = 'http://www.hcshb.gov.tw/'
HSH_URL = 'http://www.hcshb.gov.tw/home.jsp?mserno=200802220002&serno=200802220015&menudata=HcshbMenu&contlink=hcshb/ap/news.jsp'
#if only food_safety (but less data)
#HSH_URL = 'http://www.hcshb.gov.tw/home.jsp?qclass=201408280001&mserno=200802220002&serno=200802220015&menudata=HcshbMenu&contlink=hcshb/ap/news.jsp'

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
    file_path = './files/' + name.split('.')[0] + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    dl = []
    doc = do_pyquery(HSH_URL)
    # tbl = list(doc('.detail>form>table>tr').children('td>table>tr').items())
    # #tbl = tbl[3:]
    # for i in tbl[3:-4:2]:
    #     news_date = i('tr>td.main_font80').eq(3).text()
    #     #print news_date
    #     #print '--'
    #     #continue
    #     ad_year = str(int(news_date.split('/')[0]) + 1911)
    #     news_date = ad_year + '/' + news_date.split('/', 1)[-1]
    #     dt = datetime.strptime(news_date, '%Y/%m/%d')
    #     if dt.date() < since_date:
    #         break

    #     news_title = i('tr>td.main_font80').eq(1).text()
    #     news_url = PREFIX + i('tr>td>a').attr('href')
    #     news_doc = do_pyquery(news_url)
    #     print dt.date()
    #     print news_title

    #     print news_doc('p.main_font80').text()
    #     #print i.eq(1)('td').eq(3).text()
    #     print '@attach:'
    #     if u'相關附件' in i.text():
    #         print 'yyyyy'
    #     print '---'
    #     #break

    tbl = list(doc('.detail>form>table>tr').children('td>table>tr').items())
    #tbl = tbl[3:]
    dl = []
    for i in tbl[3:-4:2]:
        news_date = i('tr>td.main_font80').eq(3).text()
        #print news_date
        #print '--'
        #continue
        ad_year = str(int(news_date.split('/')[0]) + 1911)
        news_date = ad_year + '/' + news_date.split('/', 1)[-1]
        dt = datetime.strptime(news_date, '%Y/%m/%d')
        if dt.date() < since_date:
            break

        news_title = i('tr>td.main_font80').eq(1).text()
        news_url = PREFIX + i('tr>td>a').attr('href')
        #news_url = 'http://www.hcshb.gov.tw/home.jsp?mserno=200802220002&serno=200802220015&menudata=HcshbMenu&contlink=hcshb/ap/news_view.jsp&dataserno=201704190002'
        news_doc = do_pyquery(news_url)
        #print dt.date()
        #print news_title

        content = news_doc('p.main_font80').text()
        #print i.eq(1)('td').eq(3).text()
        #print '@attach:'
        if os.path.exists(FILES_DIR):
            shutil.rmtree(FILES_DIR)
        os.makedirs(FILES_DIR)
        if u'相關附件' in news_doc('.main_title80').text():
            #print 'vvvvvvvv'
            for f in news_doc('.main_font80').children('a').items():#('a').attr('href')
                file_url = PREFIX + f('a').attr('href')
                file_name = f('a').text()
                #print file_url
                download_file(file_url, file_name)
                
        #files_content = file_to_text(FILES_DIR)

        date = datetime.strftime(dt, '%Y-%m-%d')
        ut = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        hashcode = hashlib.md5(('hsh'+ news_title + date).encode("utf-8")).hexdigest()
        d = {'url': news_url, 'content': news_title + content, 'date': date, 'updatetime': ut, 'hashcode': hashcode}

        dl.append(d)

    return dl

if __name__ == '__main__':
    since_date = datetime(2018, 1, 12).date()
    pp().pprint(dump(since_date))
