from mprorp.db.dbDriver import *
from mprorp.db.models import *

from readability.readability import Document as Doc
import urllib.request
from mprorp.crawler.utils import *
import json
import html

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from mprorp.celery_app import app
from mprorp.controller.logic import *

@app.task
def findFullText(doc_id): #, wks):
    [url,meta] = select([Document.guid,Document.meta], Document.doc_id == doc_id).fetchone()
    print(url)

    try:
        """
        urllib.request.urlopen(url)
        html_source = urllib.request.urlopen(url).read() #send_get_request(url)
        #print(html)
        doc = Doc(html_source)
        readable_content = doc.summary()
        readable_title = doc.short_title()
        print(readable_title)

        readable_stripped = strip_tags(readable_content)
        readable_stripped = to_plain_text(readable_stripped)
        print(readable_stripped)
        """

        req_url = 'https://www.readability.com/api/content/v1/parser?token=08e612cb0d3f95db2090b87d3d758efc75fb314b&url='+url
        print(req_url)
        res = send_get_request(req_url) # urllib.request.urlopen(url).read().decode('unicode-escape')# send_get_request(url).decode('unicode-escape')
        json_obj = json.loads(res)

        #print(res)

        if "error" in json_obj:
            #need logging
            return;
        if "title" in json_obj:
            print(json_obj["title"])
        content = json_obj["content"]
        content = html.unescape(content)
        #print(content)
        stripped = strip_tags(content)
        stripped = to_plain_text(stripped)
        print(stripped)


        pos = url.find('//')
        publisher_url = url[:pos]+'//'+json_obj["domain"]
        meta["publisher"]['url'] = publisher_url

        #print(meta)

        document = Document(doc_id=doc_id, doc_source=content, stripped=stripped, meta=meta, status=1)
        update(document)
        router_func(doc_id, 1)


        # wks.insert_row([url,json_obj["title"],readable_title,readable_stripped,stripped], 1)
        #exit()
    except BaseException:
        print('error with url: '+url);


if __name__ == '__main__':
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('gspreadauth.json', scope)
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key('1jE_kKLC0us74INWi26Pw3Jh1EsvFaHqYZmcYkfAzdgY').sheet1

    articles = select(Document.doc_id, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()
    #articles = select(Document.doc_id, Document.guid == 'http://u-news24.com/archives/18306').fetchall()
    for article_id in articles:
        findFullText(article_id[0], wks)
    #print(articles)
    # delete("documents",Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8')
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))
