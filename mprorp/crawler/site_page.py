from mprorp.db.dbDriver import *
from mprorp.db.models import *

from readability.readability import Document as Doc
import urllib.request
from mprorp.crawler.utils import send_get_request, strip_tags
import json
import html
import re


def findFullText(doc_id):
    #try:
        [url,meta] = select([Document.guid,Document.meta], Document.doc_id == doc_id).fetchone()
        print(url)
        """
        html = urllib.request.urlopen(url).read() #send_get_request(url)
        #print(html)
        doc = Doc(html)
        content = doc.summary()
        readable_title = doc.short_title()
        print(readable_title)
        print(content)
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


        lines = stripped.split("\n")
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]

        stripped = "\n".join(lines)
        print(stripped)


        pos = url.find('//')
        publisher_url = url[:pos]+'//'+json_obj["domain"]
        meta["publisher"]['url'] = publisher_url

        #print(meta)

        document = Document(doc_id=doc_id, doc_source=content, stripped=stripped, meta=meta, status=1)
        update(document)

        #exit()
    #except BaseException:
        #print('connetcion error');


if __name__ == '__main__':
    #print('"Hello,\\nworld!"'.decode('string_escape'))
    #exit()
    articles = select(Document.doc_id, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()
    #articles = select(Document.doc_id, Document.guid == 'http://u-news24.com/archives/18306').fetchall()
    for article_id in articles:
        findFullText(article_id[0])
    #print(articles)
    # delete("documents",Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8')
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))
