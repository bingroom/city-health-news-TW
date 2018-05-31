#-*- coding: utf-8 -*-
import requests
import urllib2
import pprint
from datetime import date, datetime
from pyquery import PyQuery as pq


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
    print link, name
    file_content = get_content(link)

    file_path = './files/' + name
    f = open(file_path, 'wb')
    f.write(file_content)
    f.close()


#PREFIX = 'http://health.gov.taipei'
#POSTFIX = '&tabid=36&mid=442'
NTPE_URL = 'http://www.health.ntpc.gov.tw'

doc = do_pyquery(NTPE_URL)#pq(url=link)
for i in doc('.panel.panel-default').items():#doc(u'#焦點新聞 > div > div').items():
    news_date = i('#list_date').text()
    dt = datetime.strptime(news_date, "%Y-%m-%d")
    if dt < datetime(2017, 5, 15):
        break
    
    news_title = i('#list_title').text()
    print news_title, news_date
    news_url = NTPE_URL + i('.panel-body>a').attr('href')
    print news_url

    news_doc = do_pyquery(news_url)
    print news_doc('#is_content').text()

    files = []
    for pdf in news_doc('a').items():
        files.append(pdf.attr('href'))
    for img in news_doc('img').items():
        files.append(img.attr('src'))
    for f in files:
        if f != None and is_attachment(f):
            file_name = f.rsplit('/')[-1]
            infix = f.rsplit('/', 1)[0]#.split(NTPE_URL)[-1]
            #print NTPE_URL
            #print infix
            file_url = NTPE_URL + infix + '/' + urllib2.quote(file_name.encode('utf-8'))
            print file_url
            download_file(file_url, file_name)


    #news_date = i('div > div > .panel-heading > h4 > a > #list_date').text()

    print '---'
    #print '@', news_date, '@'