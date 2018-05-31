import os
import base64
from elasticsearch import Elasticsearch
import openxmllib
import traceback
import xlrd

#dir_path = './city_news/files/'
    
def file_to_text(dir_path):
    #{'host': '172.16.7.3', 'port': 9200}
    #{'host': '175.98.115.40', 'port': 9200}
    es = Elasticsearch([{'host': '172.16.7.3', 'port': 9200}], max_retries=10, retry_on_timeout=True)

    list_files = os.listdir(dir_path)
    text_list = []
    for f in list_files:
        print '>>>>>>>', f
        if '.pdf' in f.lower() or '.doc' in f.lower():
            fin = open(dir_path + f, 'rb')
            content = fin.read()
            fin.close()
            data = base64.b64encode(content).decode('ascii')
            body = {'data': data}
            #print data
            
            #print '!!!!!!!!!', es.cat.client
            result = es.index(index='ingest', doc_type='attachment', id=0, pipeline='attachment', body={'data': data})
            doc = es.get(index='ingest', doc_type='attachment', id=0, _source_exclude=['data']) #result['_id']
            #print doc
            text = doc['_source']['attachment']['content']

        elif '.docx' in f.lower() or '.ppt' in f.lower():
            try:
                #filetype = 'application/unknown'#magic.from_file(dir_path + f, mime=True)
                #print filetype
                doc = openxmllib.openXmlDocument(dir_path + f)
                text = doc.indexableText(include_properties=False)
            except:
                print '!!! fail !!!'
                traceback.print_exc()
                continue

        elif '.xls' in f.lower():
            wb = xlrd.open_workbook(dir_path + f)
            sh = wb.sheet_by_index(0)
            text = ""
            for n in range(sh.nrows):
                for i in range(sh.ncols):
                    data = u"{0}".format(sh.cell_value(n,i))
                    text += data + " "
                text += "\n"
            #print text
        else:
            print '!!! non-supported format !!!'
            continue
        #print content
        #print '--------'
        #continue
        #if content == None or len(content) == 0:
        #    continue
        #print text
        text_list.append(text)
        print '-----'

    return text_list


if __name__ == '__main__':
    file_to_text('./files/')