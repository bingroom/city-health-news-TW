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
import mechanize
from bs4 import BeautifulSoup

FILES_DIR = './files/'
PREFIX = 'https://www.cichb.gov.tw/news/'
#CYI_URL = 'https://www.cichb.gov.tw/news/'
CYI_URL = 'https://www.cichb.gov.tw/news/indexpda.asp'

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
            content = urllib2.urlopen(url).read()#requests.get(url, timeout=5).content 
        except:
            content = None
            print '...retry connection'
            continue    
    return content

def do_pyquery(link, max_retry=10):
    BIG5_PARSER = lxml.html.HTMLParser(encoding='big5')
    doc = None
    retry = 0
    while doc == None:
        try:
            retry += 1
            if retry >= max_retry:
                break
            doc = pq(lxml.html.fromstring(get_content(link), parser=BIG5_PARSER))
    
        except: 
            doc = None
            print '...retry doing pyquery'
            continue
    return doc

def download_file(link, name):
    #print link, name
    file_content = get_content(link)
    if file_content == None:
        return
    file_ext = link.rsplit('.')[-1]
    #raw_name = name.rsplit('.')[0]
    file_path = './files/' + name + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump_old(since_date):
    dl = []
    # br = mechanize.Browser()

    # br.set_handle_robots(False)
    # br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    # br.open(CYI_URL)#"https://www.cichb.gov.tw/news/list_all.asp?cat_id=1"

    url = 'https://www.cichb.gov.tw/news/indexpda.asp'
    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
    headers = { 'User-Agent' : user_agent }
    req = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(req)
    page = response.read()
    print page
    # soup = BeautifulSoup(br.response().read(), 'lxml')
    # n = 0
    # for i in soup.find_all():#find_all('ul')[13].find_all('li'):
    #     print '======', n
    #     n += 1
    #     print i.text
    #     # print i.find('a')['href']
    #     # print i.find('a')['title']
    #     # page_url = PREFIX + i.find('a')['href']
    #     # page_soup = BeautifulSoup(get_content(page_url), 'lxml')
    #     # for ii in page_soup.find_all('p'):
    #     #     print ii.text
    #     break

    return dl

def dump(since_date):
    dl = []
    doc = do_pyquery(CYI_URL)
    tbl = list(doc('table>tr').items())
    for i in tbl[2:-2:2]:
        news_date = i('font').text().strip()
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        if dt.date() < since_date:
            break
        news_url = PREFIX + i('a').attr('href').split('./', 1)[1]
        #news_url = 'https://www.cichb.gov.tw/news/news_detailpda.asp?news_dtl_id=5568'
        print news_date, news_url
        
        news_doc = do_pyquery(news_url)
        news_title = news_doc('table>tr').eq(2).text().split(u'主旨', 1)[-1]
        content = news_doc('table>tr>td>p').text()

        print news_title, news_date
        print content
        print '@attach:'
        for f in news_doc('tr>td').items():
            #print f.text()
            if u'檔案下載' in f.text():
                for ff in f('td>a').items():
                    file_name = ff.attr('title')
                    file_url = PREFIX + ff.attr('href')
                    print file_name, file_url
                    download_file(file_url, file_name)
                    print '@@@'
        print '--'
        #break
    #print get_content(CYI_URL)
    #soup = BeautifulSoup(get_content(CYI_URL), 'lxml')
    #print soup.text
    # for i in doc('div.md_middle > div > div > div > table > tbody > tr').items():
    #     news_date = i('td').eq(2).text()#.encode('utf-8')
    #     dt = datetime.strptime(news_date, '%Y-%m-%d')
    #     #if dt.date() < since_date:
    #     #    break
    #     news_url = i('td').eq(1)('a').attr('href')
    #     if PREFIX not in news_url:
    #         continue
        
    #     news_title = i('td').eq(1).text()
    #     news_doc = do_pyquery(news_url)
    #     print news_date, news_title
        
    #     content = news_doc('div.ptcontent.clearfix.floatholder').remove('.itemattr').text()
    #     print '--'

    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
