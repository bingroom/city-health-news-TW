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

FILES_DIR = './files/'
#PREFIX = 'http://web.kinmen.gov.tw/'
#KMN_URL = 'http://web.kinmen.gov.tw/Layout/sub_D/News_NewsListAll.aspx?frame=75&DepartmentID=32&LanguageType=1&CategoryID=128'
PREFIX = 'http://phb.kinmen.gov.tw/'
KMN_URL = 'http://phb.kinmen.gov.tw/News.aspx?n=87FB8DD4C759A8B5&sms=A2C62D68901B977C'

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
    #file_ext = 'doc'
    file_path = './files/' + name# + '.' + file_ext
    print file_path
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()

def dump(since_date):
    dl = []
    doc = do_pyquery(KMN_URL)
    #print doc
    #tbl = list(doc('#ctl00_ContentPlaceHolder1_News_ListAllPageGridView1_GridView1 > tr').items())
    #tbl = list(doc('table#table_0').items())
    #print doc('div.in > table > tbody').children()
    tbl = list(doc('div.in > table > tbody').children().items())
    for i in tbl[1:-1]:#.children('td.mc').items():
        news_date = i('td').eq(2).text()
        ad_year = str(int(news_date.split('-')[0]) + 1911)
        news_date = ad_year + '-' + news_date.split('-', 1)[-1]
        dt = datetime.strptime(news_date, '%Y-%m-%d')
        if dt.date() < since_date:
            break
        news_title = i('td').eq(1).text()
        news_url = PREFIX + i('td').eq(1)('a').attr('href')
        
        print news_date
        print news_title, news_url
        news_doc = do_pyquery(news_url)
        temp = news_doc.clone()
        content = temp('#page_matter').remove('div').text()
        if u'發佈單位：衛生局' in content:
            content = content.split(u'發佈單位：衛生局', 1)[1]
        content = content.lstrip()
        print content
        
        
        for f in news_doc('#page_matter>div').items():
            #if u'相關檔案' not in f.text():
            if not(f.find('a')):
                continue
            print '@attach:'
            for ff in f('a').items():
                file_url = ff.attr('href')
                file_name = ff.text()
                print file_name, file_url
                download_file(file_url, file_name)
            #print '@@'
        print '--'
        # news_date = i('span.date.float-right').text()
        # news_date = news_date[news_date.find('[')+1:news_date.find(']')].strip()
        # dt = datetime.strptime(news_date, '%Y-%m-%d')
        # if dt.date() < since_date:
        #     break
        # news_url = i('span.ptname>a').attr('href')
        # if PREFIX not in news_url:
        #     continue
        # news_title = i('span.ptname>a').text()
        # print news_date, news_title
        # #news_url = 'http://www.ttshb.gov.tw/files/14-1000-1257,r12-1.php?Lang=zh-tw'
        # news_doc = do_pyquery(news_url)
        # content = news_doc('div.ptcontent').remove('.itemattr').text()
        # print content
        
        # for f in news_doc('#Dyn_2_2 > div > div > div >div >div.mm_01> table.baseTB>tr').items():
        #     if f.find('a'):
        #         print '@attach:'
        #         file_name = f('td>div>span').eq(1)('a').text()
        #         file_url = PREFIX + f('td>div>span').eq(1)('a').attr('href')
        #         print file_name, file_url
        #         download_file(file_url, file_name)
        #     #print '@@'
        # #print news_doc()
        # print '--'
        # #break

    return dl

if __name__ == '__main__':
    since_date = datetime(2017, 5, 27).date()
    pp().pprint(dump(since_date))
